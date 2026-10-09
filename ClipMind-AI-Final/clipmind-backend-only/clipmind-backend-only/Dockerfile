# ClipMind AI — Backend Dockerfile
# Python 3.10 slim base (halka image, Whisper/torch ke liye kaafi hai)
FROM python:3.10-slim

# ffmpeg zaroori hai — Whisper transcription isse hi audio extract karta hai
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Pehle sirf requirements copy karo — Docker layer caching se baar-baar
# `pip install` nahi chalega jab tak dependencies badlein na
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ab poora application code copy karo
COPY . .

# Uploads aur SQLite DB ke liye folder (volume isi path par mount hoga)
RUN mkdir -p /app/uploads

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
