FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (layer caching)
COPY mcp-servers/rag-api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy brain system and config from project root context
COPY brain/ /app/brain/
COPY config/ /app/config/

# Copy server
COPY mcp-servers/rag-api/server.py .

ENV PYTHONPATH=/app

EXPOSE 8100

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8100"]
