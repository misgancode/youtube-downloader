# Video Downloader — GitHub + Cloud

## Local
pip install -r requirements.txt
python app.py

## GitHub
git init
git add .
git commit -m "Initial cloud-ready downloader"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main

## Docker
docker build -t video-downloader .
docker run --rm -p 8080:8080 video-downloader

Use only for content you are authorized to download and in accordance with the source site's terms. For public deployment, add authentication, rate limiting, abuse protection, cleanup, and a job queue. Cloud providers may restrict CPU, bandwidth, storage, and long-running requests.
