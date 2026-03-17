# MusicSync Frontend

React + Vite frontend for the YouTube Music Playlist Downloader.

## Run

1. **Start the API backend** (in project root):
   ```bash
   cd ..
   source venv/bin/activate
   python api.py
   ```

2. **Start the frontend**:
   ```bash
   npm run dev
   ```

3. Open http://localhost:5173

The frontend proxies `/api` requests to the backend at `localhost:8000`.
