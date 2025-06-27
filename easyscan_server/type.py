from pydantic import BaseModel
from typing import Optional

# Request model for setting a URL
class SetURLRequest(BaseModel):
    """
    Represents the request body for setting a URL for a given key.
    The 'url' field contains the actual URL string.
    The 'name' field is optional and provides a human-readable name for the URL.
    """
    url: str
    name: Optional[str] = None

# Response model for getting a URL
class GetURLResponse(BaseModel):
    """
    Represents the response body when retrieving a URL.
    Includes the key and the associated URL.
    """
    key: str
    url: str
    name: Optional[str] = None # Added name field

# Response model for confirming a URL has been set
class SetURLResponse(BaseModel):
    """
    Represents the response body after a URL has been successfully set.
    Confirms the key, the URL that was set, and a success status.
    """
    key: str
    url: str
    name: Optional[str] = None # Added name field
    success: bool
