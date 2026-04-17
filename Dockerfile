FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 streamlit

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY main.py recommender.py data_loader.py utils.py sample_data.csv .
RUN mkdir -p .streamlit
COPY .streamlit/config.toml .streamlit/

RUN chown -R streamlit:streamlit /app
USER streamlit

HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/_stcore/health || exit 1

EXPOSE 8080

CMD ["streamlit", "run", "main.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.headless=true"]
