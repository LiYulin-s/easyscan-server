from fastapi import FastAPI, HTTPException, Request # Import Request
from fastapi.responses import RedirectResponse, HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates # Import Jinja2Templates

from fakeredis.aioredis import FakeRedis

from pydantic import BaseModel
from redis.asyncio import Redis
import os 
from pathlib import Path

from .type import SetURLRequest, GetURLResponse, SetURLResponse # Import updated models from type.py
from .domain import Domain, URLData # Import URLData from domain

import asyncio
import json

app = FastAPI()

# Get Redis URL from environment variable, default to localhost for development

domain = None

if os.getenv("USE_REAL_REDIS") is not None:
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
    domain = Domain(redis= Redis.from_url(redis_url))

else:
    # Use FakeRedis for testing or development purposes
    domain = Domain(redis=FakeRedis())

# Initialize Jinja2Templates to load templates from the "templates" directory
# Use dynamic path resolution to handle both development and installed package scenarios
current_dir = Path(__file__).parent
templates_dir = current_dir / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Store current clients connected to SSE for a specific key
# In a production environment, this would need more robust management
# (e.g., using a message queue, Redis Pub/Sub, or a dedicated connection manager)
CONNECTED_SSE_CLIENTS = {}

@app.get("/{key}", response_model=GetURLResponse) # Use GetURLResponse
async def get(key: str):
    """
    Retrieves the URL associated with a given key.
    Returns 404 if the key is not found.
    """
    url_data = await domain.get(key)
    if url_data is None:
        raise HTTPException(status_code=404, detail=f"Key '{key}' not found or no URL associated.")
    return GetURLResponse(
        key=key,
        name=url_data.name, # Return the stored name
        url=url_data.url # Access the 'url' attribute of the URLData object
    )

@app.get("/{key}/redirect")
async def redirect(key: str):
    """
    Redirects to the URL stored against the given key.
    """
    url_data = await domain.get(key)
    # Check if url_data exists and contains a valid URL
    if url_data and url_data.url:
        return RedirectResponse(url=url_data.url)
    else:
        raise HTTPException(status_code=404, detail=f"URL for key '{key}' not found or invalid for redirection.")

@app.post("/", response_model=SetURLResponse) # Use SetURLResponse
async def set(request_body: SetURLRequest): # Renamed 'request' to 'request_body' to avoid conflict with fastapi.Request
    """
    Sets a new key-URL-name pair and notifies any connected SSE clients for that key.
    The request body expects 'url' and 'name' fields.
    """

    key = domain.generate_key()

    url_data = URLData(url=request_body.url, name=request_body.name)

    await domain.insert(key, url_data)

    if key in CONNECTED_SSE_CLIENTS:
        for queue in CONNECTED_SSE_CLIENTS[key]:
            await queue.put(url_data) # Put the whole URLData object

    return SetURLResponse(
        key=key,
        url=url_data.url, 
        name=url_data.name,
        success=True
    )


@app.post("/{key}", response_model=SetURLResponse)
async def set_with_key(key: str, request_body: SetURLRequest): # Renamed function to avoid conflict
    """
    Updates an existing key-URL-name pair and notifies any connected SSE clients for that key.
    The request body expects 'url' and 'name' fields.
    """
    prev_url_data = await domain.get(key)

    if prev_url_data is None:
        raise HTTPException(status_code=404, detail=f"Key '{key}' not found or no URL associated.")
    
    # Update the existing URLData object or create a new one with updated fields
    # If a new name is provided, use it; otherwise, retain the previous name
    # If a new URL is provided, use it; otherwise, retain the previous URL
    updated_url_data = URLData(
        url=request_body.url or prev_url_data.url, # Use new URL if provided, else old URL
        name=request_body.name or prev_url_data.name # Use new name if provided, else old name
    )

    await domain.insert(key, updated_url_data) # Overwrite with updated data

    # Notify connected SSE clients about the update
    if key in CONNECTED_SSE_CLIENTS:
        for queue in CONNECTED_SSE_CLIENTS[key]:
            await queue.put(updated_url_data) # Put the whole updated URLData object

    return SetURLResponse(
        key=key,
        url=updated_url_data.url, 
        name=updated_url_data.name,
        success=True
    )

@app.get("/{key}/qrcode", response_class=HTMLResponse)
async def qrcode(key: str, request: Request): # Add 'request: Request' parameter
    """
    Generates an HTML page displaying a QR code for the URL stored against the key.
    The QR code is generated using QRCode.js on the client-side.
    This page includes JavaScript to establish an SSE connection for real-time updates.
    The HTML content is now rendered from a Jinja2 template.
    """
    # Retrieve the initial URLData object associated with the key
    url_data = await domain.get(key)

    # Use default empty string or "Unnamed Link" if no URL data or specific field exists
    initial_url = url_data.url if url_data and url_data.url else ""
    initial_name = url_data.name if url_data and url_data.name else "Unnamed Link" 

    # Render the HTML template with the dynamic values
    return templates.TemplateResponse(
        "qrcode.html",  # Name of the template file in the 'templates' directory
        {
            "request": request, # Jinja2 templates require the request object
            "key": key,
            "initial_url": initial_url,
            "initial_name": initial_name # Pass initial_name to the template
        }
    )

@app.get("/sse/{key}")
async def sse(key: str):
    """
    Server-Sent Events endpoint to push real-time updates of the URL and Name for a given key.
    Clients will connect to this endpoint to receive updates when the URL or Name changes.
    """
    # Use an asyncio.Queue to hold events for this client
    # This acts as a simple in-memory queue for new URLData objects
    queue = asyncio.Queue()

    # Register the client's queue
    if key not in CONNECTED_SSE_CLIENTS:
        CONNECTED_SSE_CLIENTS[key] = []
    CONNECTED_SSE_CLIENTS[key].append(queue)

    async def event_generator():
        # Keep track of the last URL and Name sent to this client to avoid duplicates
        last_sent_data = {} 

        try:
            # Send the initial URL and Name as the first event
            initial_url_data = await domain.get(key)
            initial_url = initial_url_data.url if initial_url_data else ""
            initial_name = initial_url_data.name if initial_url_data else "Unnamed Link"

            if initial_url: # Only send if there's an initial URL
                initial_payload = {"url": initial_url, "name": initial_name}
                yield f"data: {json.dumps(initial_payload)}\n\n"
                last_sent_data = initial_payload

            while True:
                # Wait for a new URLData object to be pushed into the queue
                try:
                    # Timeout helps to ensure connection is alive or to poll if no events
                    new_url_data = await asyncio.wait_for(queue.get(), timeout=10.0)

                    current_payload = {"url": new_url_data.url, "name": new_url_data.name}

                    # Only send if the data has actually changed
                    if current_payload != last_sent_data:
                        yield f"data: {json.dumps(current_payload)}\n\n"
                        last_sent_data = current_payload
                    queue.task_done() # Mark the task as done for the queue

                except asyncio.TimeoutError:
                    # If timeout occurs, re-fetch the current URL and Name from the domain
                    # This acts as a basic polling mechanism if the post endpoint isn't hit
                    current_url_data = await domain.get(key)
                    current_url = current_url_data.url if current_url_data else ""
                    current_name = current_url_data.name if current_url_data else "Unnamed Link"
                    
                    current_payload = {"url": current_url, "name": current_name}

                    # Only send if the data has actually changed
                    if current_payload != last_sent_data:
                        yield f"data: {json.dumps(current_payload)}\n\n"
                        last_sent_data = current_payload
                except Exception as e:
                    print(f"Error in SSE generator for key {key}: {e}")
                    break # Break the loop on error

        except asyncio.CancelledError:
            print(f"SSE client for key {key} disconnected gracefully.")
        finally:
            # Clean up when the client disconnects
            if key in CONNECTED_SSE_CLIENTS and queue in CONNECTED_SSE_CLIENTS[key]:
                CONNECTED_SSE_CLIENTS[key].remove(queue)
                if not CONNECTED_SSE_CLIENTS[key]:
                    del CONNECTED_SSE_CLIENTS[key]


    return StreamingResponse(event_generator(), media_type="text/event-stream")
