import uvicorn
import typer

def main(
    host: str = typer.Option("0.0.0.0", "--host", help="Host to bind the server to"),
    port: int = typer.Option(8000, "--port", help="Port to bind the server to")
):
    """Start the easyscan_server application."""
    uvicorn.run("easyscan_server.main:app", host=host, port=port)

if __name__ == "__main__":
    typer.run(main)
