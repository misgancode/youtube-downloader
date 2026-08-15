FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    ca-certificates \
    unzip \
    nodejs \
    npm \
    libcairo2-dev \
    libpango1.0-dev \
    libjpeg62-turbo-dev \
    libgif-dev \
    librsvg2-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deno.land/install.sh | sh -s -- -y

ENV PATH="/root/.deno/bin:${PATH}"
ENV PYTHONUNBUFFERED=1
ENV DENO_NO_PROMPT=1
ENV DENO_NO_UPDATE_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bgutil-ytdlp-pot-provider/package.json bgutil-ytdlp-pot-provider/package-lock.json bgutil-ytdlp-pot-provider/deno.lock ./bgutil/
COPY bgutil-ytdlp-pot-provider/types ./bgutil/types
COPY bgutil-ytdlp-pot-provider/src ./bgutil/src

RUN cd /app/bgutil && npm ci --omit=dev --no-audit --no-fund

COPY . .

CMD ["sh","-c","deno run --allow-env --allow-net --allow-ffi=/app/bgutil/node_modules --allow-read=/app/bgutil/node_modules /app/bgutil/src/main.ts & exec gunicorn app:app --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 2 --timeout 900"]
