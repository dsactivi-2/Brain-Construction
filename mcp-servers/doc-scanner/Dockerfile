FROM python:3.12-slim
WORKDIR /app
COPY mcp-servers/doc-scanner/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY brain/ /app/brain/
COPY config/ /app/config/
COPY mcp-servers/doc-scanner/server.py .
ENV PYTHONPATH=/app
EXPOSE 8101
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8101"]
