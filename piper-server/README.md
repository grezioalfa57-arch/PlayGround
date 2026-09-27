# 🔊 FRIDAY Piper TTS Server (opsional)

Memberi F.R.I.D.A.Y. **suara neural Bahasa Indonesia** (`id_ID-news_tts-medium`)
yang jauh lebih natural daripada suara bawaan browser. 100% lokal, offline, gratis.

FRIDAY tetap jalan normal **tanpa** server ini (pakai suara browser).
Kalau server terdeteksi di `http://127.0.0.1:5002`, FRIDAY otomatis
menawarkannya di pemilih mesin suara. Tanpa daftar, tanpa API key.

## Cara pakai (Linux)

```bash
# 1. Install sekali saja:
pip install piper-tts
sudo apt install espeak-ng        # Debian/Ubuntu (dibutuhkan piper)

# 2. Jalankan (otomatis unduh voice ±60 MB saat pertama kali):
chmod +x run.sh
./run.sh
# atau ganti port:  PORT=5003 ./run.sh
```

## Cek

```bash
curl http://127.0.0.1:5002/api/health
curl -X POST http://127.0.0.1:5002/api/tts \
  -H 'Content-Type: application/json' \
  -d '{"text":"Halo Boss, sistem Friday siap."}' --output halo.wav
```

## API

| Endpoint      | Fungsi                                            |
|---------------|---------------------------------------------------|
| `GET /api/health` | `{"ok":true,"engine":"piper","model":"…"}`  |
| `POST /api/tts`   | body `{"text":"…"}` (maks 800 char) → `audio/wav` |

## Catatan

- Binding hanya `127.0.0.1` (tidak terekspos ke jaringan) — aman.
- Deployment statis (OMGithub) tidak menjalankan server ini;
  ia berjalan di perangkatmu sendiri, berdampingan dengan tab FRIDAY.
