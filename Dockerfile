FROM python:3.13.5-slim-bookworm

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Copy the application
WORKDIR /app
COPY . .

# Install dependencies and the application using uv
RUN uv sync --frozen

EXPOSE 8000

# Run the application using uv
CMD ["uv", "run", "python", "-m", "easyscan_server", "--host", "0.0.0.0", "--port", "8000"]