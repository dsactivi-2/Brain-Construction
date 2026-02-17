FROM python:3.12-slim
WORKDIR /app
COPY brain/hipporag_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download de_core_news_md && \
    python -m spacy download en_core_web_sm
COPY brain/ /app/brain/
COPY config/ /app/config/
COPY brain/hipporag_service/http_server.py .
ENV PYTHONPATH=/app
EXPOSE 8102
CMD ["uvicorn", "http_server:app", "--host", "0.0.0.0", "--port", "8102"]
