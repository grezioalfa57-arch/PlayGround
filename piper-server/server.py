#!/usr/bin/env python3
"""F.R.I.D.A.Y. Piper TTS Server — stdlib only, no pip dependencies.

Exposes the local Piper neural TTS engine to the static FRIDAY web app:

  GET  /api/health  -> {"ok": true, "model": "...", "engine": "piper"}
  POST /api/tts     -> {"text": "..."} returns audio/wav bytes

Run via run.sh (checks piper binary + downloads the Indonesian voice),
or manually:
  python3 server.py --port 5002 --model voices/id_ID-news_tts-medium.onnx
"""
import argparse
import json
import os
import subprocess
import tempfile
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODEL = ""
PIPER_CMD = "piper"
MAX_CHARS = 800


class Handler(BaseHTTPRequestHandler):
    server_version = "FridayPiper/1.0"

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/api/health":
            self._json({"ok": True, "engine": "piper", "model": os.path.basename(MODEL)})
        else:
            self._json({"ok": False, "error": "not found",
                        "usage": "POST /api/tts {text} | GET /api/health"}, 404)

    def do_POST(self):
        if urllib.parse.urlparse(self.path).path != "/api/tts":
            self._json({"ok": False, "error": "not found"}, 404)
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
        except ValueError:
            length = 0
        if length <= 0 or length > 64 * 1024:
            self._json({"ok": False, "error": "bad body"}, 400)
            return
        try:
            text = json.loads(self.rfile.read(length)).get("text", "")
        except Exception:
            self._json({"ok": False, "error": "bad json"}, 400)
            return
        text = " ".join(str(text).split())[:MAX_CHARS]
        if not text:
            self._json({"ok": False, "error": "empty text"}, 400)
            return
        if not os.path.exists(MODEL):
            self._json({"ok": False, "error": "model not found: " + MODEL}, 500)
            return
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp.close()
        try:
            p = subprocess.run(
                [PIPER_CMD, "--model", MODEL, "--output_file", tmp.name],
                input=text.encode("utf-8"), capture_output=True, timeout=120)
            if p.returncode != 0 or not os.path.exists(tmp.name):
                self._json({"ok": False, "error": "piper failed: " +
                            p.stderr.decode()[-300:]}, 500)
                return
            with open(tmp.name, "rb") as f:
                wav = f.read()
            if len(wav) < 100:
                self._json({"ok": False, "error": "piper produced no audio"}, 500)
                return
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "audio/wav")
            self.send_header("Content-Length", str(len(wav)))
            self.end_headers()
            self.wfile.write(wav)
        except subprocess.TimeoutExpired:
            self._json({"ok": False, "error": "piper timeout"}, 500)
        finally:
            try:
                os.unlink(tmp.name)
            except OSError:
                pass

    def log_message(self, fmt, *args):
        print("[piper-server]", fmt % args, flush=True)


def main():
    global MODEL, PIPER_CMD
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=5002)
    ap.add_argument("--model", default="voices/id_ID-news_tts-medium.onnx")
    ap.add_argument("--piper-cmd", default=os.environ.get("PIPER_CMD", "piper"))
    args = ap.parse_args()
    MODEL = args.model if os.path.isabs(args.model) else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), args.model)
    PIPER_CMD = args.piper_cmd
    srv = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"[piper-server] listening on http://127.0.0.1:{args.port}", flush=True)
    print(f"[piper-server] model: {MODEL}", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
