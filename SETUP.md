# Step-by-Step Setup Guide

Follow these steps to get the YouTube Music Playlist Downloader running on your computer.

---

## Step 1: Install Prerequisites

### Python 3
- **macOS:** `brew install python3` (or use the version from python.org)
- **Windows:** Download from [python.org](https://python.org)
- Verify: `python3 --version` (should be 3.9 or newer)

### Node.js (for the web UI)
- **macOS:** `brew install node`
- **Windows:** Download from [nodejs.org](https://nodejs.org)
- Verify: `node --version`

### FFmpeg (required for audio conversion)
- **macOS:** `brew install ffmpeg`
- **Windows:** Download from [ffmpeg.org](https://ffmpeg.org) or use `winget install ffmpeg`
- Verify: `ffmpeg -version`

---

## Step 2: Open the Project Folder

```bash
cd "/Users/evie/Documents/Cursor/Music downloader"
```

(Or wherever your project is located.)

---

## Step 3: Create a Python Virtual Environment

```bash
python3 -m venv venv
```

Activate it:
- **macOS/Linux:** `source venv/bin/activate`
- **Windows:** `venv\Scripts\activate`

You should see `(venv)` in your terminal prompt.

---

## Step 4: Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 5: Install Frontend Dependencies (for the web UI)

```bash
cd frontend
npm install
cd ..
```

---

## Step 6: Configure Your Playlists

Edit `config.yaml` in the project folder.

**Option A – Add playlists via the web UI later**  
You can leave the default playlists or clear them. You’ll add URLs in the browser.

**Option B – Add playlists now in config.yaml**

```yaml
playlists:
  - id: PLxxxxxxxxxxxxxxxxxx   # From music.youtube.com/playlist?list=PLxxx
    name: My Favorites
    paused: false
```

To get a playlist ID: open the playlist on YouTube Music and copy the part after `list=` in the URL.

---

## Step 7: Configure Storage (Where Files Are Saved)

In `config.yaml`, under `storage`:

- **Save to your computer:** (default)
  ```yaml
  storage:
    local: true
    local_path: ~/Music/YouTube
  ```

- **Save to Google Drive:** See “Optional: Google Drive” below.

---

## Step 8: Run the App

**Easiest way (one command):**

```bash
./run.sh
```

Then open **http://localhost:8000** in your browser.

**Alternative (manual):**

```bash
# Build the frontend (first time only)
cd frontend && npm run build && cd ..

# Start the server
python api.py
```

Then open **http://localhost:8000**.

---

## Step 9: Use the App

1. Open http://localhost:8000 in your browser.
2. Paste a YouTube Music playlist URL in the input bar and click **Add**.
3. Click **Sync now** to download new tracks.
4. Switch between **Playlist** and **Tracks** views to see playlists or the track list.

---

## Optional: Google Drive

To save downloads to Google Drive instead of (or in addition to) your computer:

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project (or use an existing one).
3. Enable **Google Drive API**.
4. Create **OAuth 2.0 Client ID** (Desktop app).
5. Download credentials and save as `credentials.json` in the project folder.
6. In `config.yaml`:
   ```yaml
   storage:
     local: false
     google_drive: true
     drive_folder_id: ''   # Leave empty for "YouTube Music" folder at root
   ```
7. Run the app and trigger a sync. A browser window will open for you to sign in and authorize.

---

## Troubleshooting

| Problem | Solution |
|--------|----------|
| **403 / Download fails** | Make sure you’re signed into YouTube Music in Chrome (or the browser in `cookies_browser` in config). |
| **FFmpeg not found** | Install FFmpeg and ensure it’s in your PATH (`ffmpeg -version`). |
| **Port 8000 in use** | Stop the other process or change the port in `api.py`. |
| **Blank page** | Run `cd frontend && npm run build` and restart the server. |

---

## Deploy to the Web (Render)

To use the app from any browser without running it locally, see **[RENDER_SETUP.md](RENDER_SETUP.md)**.
