import os, re, shutil, subprocess, tempfile
from pathlib import Path
from flask import Flask, jsonify, render_template, request, send_file

app=Flask(__name__)
MAX_MB=int(os.environ.get("MAX_DOWNLOAD_MB","500"))
TIMEOUT=int(os.environ.get("DOWNLOAD_TIMEOUT","900"))
TMP=Path(os.environ.get("DOWNLOAD_TMP",tempfile.gettempdir()))/"yt-downloader"
TMP.mkdir(parents=True,exist_ok=True)

@app.get("/")
def index(): return render_template("index.html")

@app.get("/health")
def health():
    return jsonify(ok=True, yt_dlp=bool(shutil.which("yt-dlp")), ffmpeg=bool(shutil.which("ffmpeg")))

@app.post("/api/download")
def download():
    d=request.get_json(silent=True) or {}
    url=(d.get("url") or "").strip()
    q=d.get("quality","best")
    if not re.match(r"^https?://",url,re.I):
        return jsonify(error="Please provide a valid HTTP/HTTPS URL."),400
    if not shutil.which("yt-dlp"): return jsonify(error="yt-dlp is not installed."),500
    if not shutil.which("ffmpeg"): return jsonify(error="FFmpeg is not installed."),500

    if q=="720": fmt="bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]"
    elif q=="480": fmt="bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]"
    elif q=="audio": fmt="bestaudio[ext=m4a]/bestaudio"
    else: fmt="bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]"

    with tempfile.TemporaryDirectory(dir=TMP) as job:
        out=str(Path(job)/"%(title).100s.%(ext)s")
        cmd=["yt-dlp","--verbose","--no-playlist","--max-filesize",f"{MAX_MB}M","--restrict-filenames","--extractor-args","youtubepot-bgutilhttp:base_url=http://127.0.0.1:4416;player_client=mweb","-f",fmt,"-o",out,"--merge-output-format","mp4","--no-warnings",url]
        if q=="audio": cmd += ["-x","--audio-format","mp3"]
        try: r=subprocess.run(cmd,capture_output=True,text=True,timeout=TIMEOUT)
        except subprocess.TimeoutExpired: return jsonify(error="Download timed out."),504
        if r.returncode!=0:
            print("===== YT-DLP ERROR =====", flush=True)
            print(r.stderr[-10000:], flush=True)
            print("===== END YT-DLP ERROR =====", flush=True)
            return jsonify(error="yt-dlp could not download this video.",details=r.stderr[-3000:]),500
        files=[p for p in Path(job).iterdir() if p.is_file() and not p.name.endswith((".part",".ytdl"))]
        if not files: return jsonify(error="No output file was produced."),500
        p=files[0]
        return send_file(p,as_attachment=True,download_name=p.name,max_age=0)

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT","5000")),debug=False)
