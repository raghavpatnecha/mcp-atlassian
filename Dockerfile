# Use the original Dockerfile as base but override the entrypoint
FROM python:3.11-slim

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN uv sync --frozen --no-dev --no-editable

# Copy our HTTP server script
COPY web_server.py .

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PORT=8000
ENV HOST=0.0.0.0

# Expose port
EXPOSE 8000

# Use our HTTP server instead of the default MCP command
ENTRYPOINT ["python", "web_server.py"]