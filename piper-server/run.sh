#!/usr/bin/env bash
# F.R.I.D.A.Y. Piper TTS Server launcher (Linux).
# - Checks for the `piper` binary (or python -m piper)
# - Downloads the Indonesian voice id_ID-news_tts-medium if missing (~60 MB)
# - Starts server.py on port 5002
set -euo pipefail
cd "$(dirname "$0")"

PORT="${PORT:-5002}"
VOICE_DIR="${VOICE_DIR:-voices}"
MODEL_NAME="id_ID-news_tts-medium"
MODEL="$VOICE_DIR/$MODEL_NAME.onnx"
BASE_URL="https://huggingface.co/rhasspy/piper-voices/resolve/main/id/id_ID/news_tts/medium"

# 1. piper binary?
if command -v piper >/dev/null 2>&1; then
  PIPER_CMD="piper"
elif python3 -c "import piper" >/dev/null 2>&1; then
  PIPER_CMD="python3 -m piper"
else
  echo "ERROR: piper belum terinstall."
  echo "Install dengan:  pip install piper-tts"
  echo "Lalu butuh espeak-ng:  sudo apt install espeak-ng  (Debian/Ubuntu)"
  exit 1
fi
echo "[run] piper: $PIPER_CMD"

# 2. voice model?
mkdir -p "$VOICE_DIR"
if [[ ! -f "$MODEL" || ! -f "$MODEL.json" ]]; then
  echo "[run] mengunduh suara Indonesia ($MODEL_NAME) ~60 MB…"
  curl -sSL -o "$MODEL" "$BASE_URL/$MODEL_NAME.onnx?download=true"
  curl -sSL -o "$MODEL.json" "$BASE_URL/$MODEL_NAME.onnx.json?download=true"
  echo "[run] voice tersimpan di $VOICE_DIR/"
else
  echo "[run] voice OK: $MODEL"
fi

# 3. serve
echo "[run] FRIDAY Piper TTS → http://127.0.0.1:$PORT/api/health"
PIPER_CMD="$PIPER_CMD" exec python3 server.py --port "$PORT" --model "$MODEL" --piper-cmd "$PIPER_CMD"
