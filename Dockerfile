FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    ca-certificates \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Deno for yt-dlp's YouTube JavaScript challenge solving
RUN curl -fsSL https://deno.land/install.sh | sh -s -- -y

ENV PATH="/root/.deno/bin:${PATH}"
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh","-c","gunicorn app:app --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 2 --timeout 900"]
