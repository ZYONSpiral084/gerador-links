FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential ca-certificates \
  && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY src/gerador_links_advanced_auth.py ./
EXPOSE 5000
ENV FLASK_ENV=production
CMD ["python", "gerador_links_advanced_auth.py"]