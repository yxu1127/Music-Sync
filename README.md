# YouTube Music Playlist Downloader

Auto-detect new songs in your YouTube Music playlist, convert to WAV, and save locally or to Google Drive.

**New to the project?** See **[SETUP.md](SETUP.md)** for step-by-step setup instructions.

## Setup

### 1. Create virtual environment

```bash
cd "Music downloader"
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg (required for audio conversion)

```bash
brew install ffmpeg   # macOS
# Verify: ffmpeg -version
```

### 4. Configure

- Edit `config.yaml` with your playlist ID(s)
- Use browser auth: copy headers from YouTube Music → `headers.json` → `python convert_headers.py | ytmusicapi browser`

### 5. (Optional) Google Drive

To upload to Google Drive:

1. In [Google Cloud Console](https://console.cloud.google.com/), enable **Google Drive API**
2. Create **OAuth 2.0 Client ID** (Desktop app)
3. Download credentials → save as `credentials.json` in the project folder
4. In `config.yaml`, set `google_drive: true`
5. Optionally set `drive_folder_id` to a specific folder ID (or leave empty to create "YouTube Music" at root)
6. First run will open a browser to authorize → creates `token_drive.json`

### 6. Run

```bash
# Test auth
python main.py --test-auth

# Download new tracks (one-time)
python main.py

# Download from a specific playlist only
python main.py --playlist PLxxxxxxxx

# Run on schedule (checks every 30 min, press Ctrl+C to stop)
python run_scheduler.py
```

The schedule interval is set in `config.yaml` under `schedule.interval_minutes`.

## API (for web frontend)

Start the REST API server:

```bash
python api.py
```

Server runs at `http://localhost:8000`. Interactive docs: `http://localhost:8000/docs`

**Endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/playlists` | List configured playlists |
| GET | `/api/config` | Get config (format, paths, schedule) |
| POST | `/api/sync` | Trigger sync. Body: `{"playlist_id": "PLxxx"}` (optional) |

## Web frontend

**Option A – Single command (no Cursor needed):**

```bash
./run.sh
```

Then open **http://localhost:8000** in any browser. The script builds the frontend on first run, then starts the server.

**Option B – Dev mode (API + Vite):**

```bash
python api.py          # Terminal 1
cd frontend && npm run dev   # Terminal 2
```

Then open http://localhost:5173

## Deploy to Render (personal use)

See **[RENDER_SETUP.md](RENDER_SETUP.md)** for a step-by-step guide to host on Render and use it from any browser.
