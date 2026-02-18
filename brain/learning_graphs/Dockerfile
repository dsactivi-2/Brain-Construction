FROM python:3.12-slim
WORKDIR /app
COPY brain/learning_graphs/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY brain/ /app/brain/
COPY config/ /app/config/
COPY brain/learning_graphs/http_server.py .
ENV PYTHONPATH=/app
CMD ["uvicorn", "http_server:app", "--host", "0.0.0.0", "--port", "8103"]
