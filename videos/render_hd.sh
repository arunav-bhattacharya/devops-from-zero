#!/bin/bash
# Render one scene at 1920x1080, 30 fps, then make the web copy, poster and captions in public/video/.
# Usage: videos/render_hd.sh <file.py relative to videos/> <SceneClass> <slug> [poster_seconds]
# Audio: the Kokoro voice is levelled to -16 LUFS (spoken-word loudness) and encoded at 128 kbps AAC.
set -e
cd "$(dirname "$0")"
F=$1; S=$2; SLUG=$3; PAT=${4:-}
OUT=../public/video
MANIM=${MANIM:-/home/user/videotools/manimenv/bin/manim}
mkdir -p "$OUT"
nice -n 10 "$MANIM" --resolution 1920,1080 --frame_rate 30 --disable_caching "$F" "$S" > "/tmp/render_$SLUG.log" 2>&1 || { echo "FAIL $SLUG"; tail -15 "/tmp/render_$SLUG.log"; exit 1; }
base=$(basename "$F" .py)
SRC=media/videos/$base/1080p30/$S.mp4
nice -n 10 ffmpeg -loglevel error -y -i "$SRC" -c:v libx264 -preset slow -crf 20 -tune animation -pix_fmt yuv420p -movflags +faststart \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11" -ar 48000 -c:a aac -b:a 128k -ac 1 "$OUT/$SLUG.mp4"
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/$SLUG.mp4")
T=${PAT:-$(python3 -c "print(round($D*0.85,2))")}
ffmpeg -loglevel error -y -ss "$T" -i "$OUT/$SLUG.mp4" -frames:v 1 -vf scale=1280:-1 -q:v 3 "$OUT/$SLUG.jpg"
cp "captions/$S.vtt" "$OUT/$SLUG.vtt"
echo "$SLUG ${D%.*}s $(du -k "$OUT/$SLUG.mp4" | cut -f1)KB"
