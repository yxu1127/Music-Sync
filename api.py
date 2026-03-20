#!/usr/bin/env python3
"""FastAPI backend for the YouTube Music Playlist Downloader."""

import threading
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown hooks."""
    from src.config import setup_cloud_secrets
    setup_cloud_secrets()
    yield


app = FastAPI(
    title="YouTube Music Downloader API",
    description="API for monitoring and syncing YouTube Music playlists",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Response models ---


class PlaylistInfo(BaseModel):
    id: str
    name: str
    paused: bool = False
    thumbnail: Optional[str] = None


class SyncRequest(BaseModel):
    playlist_id: Optional[str] = None


class AddPlaylistRequest(BaseModel):
    url: Optional[str] = None
    playlist_id: Optional[str] = None
    name: Optional[str] = None


class PausePlaylistRequest(BaseModel):
    paused: Optional[bool] = None


class UpdateScheduleRequest(BaseModel):
    interval_minutes: int


class UpdateFormatRequest(BaseModel):
    format: str


class SyncSummary(BaseModel):
    playlist_id: str
    playlist_name: str
    new_count: int
    downloaded: int
    failed: int


class SyncResponse(BaseModel):
    success: bool
    total_downloaded: int
    playlists: list[SyncSummary]


class ConfigResponse(BaseModel):
    playlists: list[PlaylistInfo]
    download_format: str
    local_path: str
    google_drive_enabled: bool
    schedule_interval_minutes: int


class DownloadedTrack(BaseModel):
    video_id: str
    playlist_id: str
    playlist_name: str
    title: str
    artist: str
    downloaded_at: str


class PendingTrack(BaseModel):
    video_id: str
    playlist_id: str
    playlist_name: str
    title: str
    artist: str


# --- Endpoints ---


@app.get("/api/health")
def health():
    """Health check."""
    return {"status": "ok"}


def _extract_playlist_id(s: str) -> Optional[str]:
    """Extract playlist ID from URL or raw ID."""
    import re
    if not s or not s.strip():
        return None
    s = s.strip()
    m = re.search(r"[?&]list=([a-zA-Z0-9_-]+)", s)
    if m:
        return m.group(1)
    if s.startswith("PL") and len(s) > 5:
        return s
    return None


@app.get("/api/playlists", response_model=list[PlaylistInfo])
def list_playlists():
    """List configured playlists."""
    from src.playlist_monitor import get_playlist_thumbnail
    from src.playlist_store import get_playlists, save_playlist_thumbnail

    try:
        playlists = get_playlists()
        result = []
        for p in playlists:
            thumb = p.get("thumbnail")
            if not thumb:
                try:
                    thumb = get_playlist_thumbnail(p["id"])
                    if thumb:
                        save_playlist_thumbnail(p["id"], thumb)
                except Exception:
                    pass
            result.append(
                PlaylistInfo(
                    id=p["id"],
                    name=p.get("name", "Unknown"),
                    paused=p.get("paused", False),
                    thumbnail=thumb,
                )
            )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/playlists/{playlist_id}", response_model=PlaylistInfo)
def toggle_playlist_pause(playlist_id: str, body: PausePlaylistRequest = PausePlaylistRequest()):
    """Set paused state. Body: { \"paused\": true } to stop, { \"paused\": false } to resume."""
    from src.playlist_store import get_playlists, set_playlist_paused

    playlists = get_playlists()
    pl = next((p for p in playlists if p["id"] == playlist_id), None)
    if not pl:
        raise HTTPException(status_code=404, detail=f"Playlist {playlist_id} not found")

    paused = body.paused if body.paused is not None else not pl.get("paused", False)
    set_playlist_paused(playlist_id, paused)
    return PlaylistInfo(
        id=pl["id"],
        name=pl.get("name", "Unknown"),
        paused=paused,
        thumbnail=pl.get("thumbnail"),
    )


@app.delete("/api/playlists/{playlist_id}")
def remove_playlist(playlist_id: str):
    """Remove a playlist from config."""
    from src.playlist_store import remove_playlist as store_remove_playlist

    try:
        store_remove_playlist(playlist_id)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/playlists", response_model=PlaylistInfo)
def add_playlist(request: AddPlaylistRequest):
    """Add a playlist by URL or ID. Fetches name from YouTube if not provided."""
    from src.playlist_store import add_playlist as store_add_playlist

    playlist_id = None
    if request.url:
        playlist_id = _extract_playlist_id(request.url)
    elif request.playlist_id:
        playlist_id = request.playlist_id.strip()

    if not playlist_id:
        raise HTTPException(
            status_code=400,
            detail="Provide a YouTube playlist URL (e.g. music.youtube.com/playlist?list=PLxxx) or playlist ID",
        )

    try:
        added = store_add_playlist(playlist_id, name=request.name)
        return PlaylistInfo(
            id=added["id"],
            name=added["name"],
            paused=added.get("paused", False),
            thumbnail=added.get("thumbnail"),
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/config/schedule")
def update_schedule(body: UpdateScheduleRequest):
    """Update schedule interval (15–1440 minutes)."""
    from src.config import set_schedule_interval

    try:
        set_schedule_interval(body.interval_minutes)
        return {"success": True, "interval_minutes": body.interval_minutes}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/config/format")
def update_format(body: UpdateFormatRequest):
    """Update download format (wav or mp3)."""
    from src.config import set_download_format

    try:
        set_download_format(body.format)
        return {"success": True, "format": body.format}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/config", response_model=ConfigResponse)
def get_config():
    """Get current configuration (safe for display, no secrets)."""
    from src.config import get_download_config, get_storage_config, load_config
    from src.playlist_store import get_playlists

    try:
        config = load_config()
        playlists = get_playlists()
        download = get_download_config(config)
        storage = get_storage_config(config)
        schedule = config.get("schedule", {})

        return ConfigResponse(
            playlists=[
                PlaylistInfo(
                    id=p["id"],
                    name=p.get("name", "Unknown"),
                    paused=p.get("paused", False),
                    thumbnail=p.get("thumbnail"),
                )
                for p in playlists
            ],
            download_format=download.get("format", "wav"),
            local_path=storage.get("local_path", ""),
            google_drive_enabled=storage.get("google_drive", False),
            schedule_interval_minutes=schedule.get("interval_minutes", 30),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tracks/pending", response_model=list[PendingTrack])
def list_pending_tracks():
    """List tracks that are in playlists but not yet downloaded (queueing)."""
    from src.playlist_monitor import get_new_tracks
    from src.playlist_store import get_playlists

    try:
        playlists = get_playlists()
        result = []
        for p in playlists:
            if p.get("paused", False):
                continue
            pl_id, pl_name = p["id"], p.get("name", "Unknown")
            for t in get_new_tracks(pl_id):
                result.append(
                    PendingTrack(
                        video_id=t["videoId"],
                        playlist_id=pl_id,
                        playlist_name=pl_name,
                        title=t.get("title", "Unknown"),
                        artist=t.get("artist", ""),
                    )
                )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sync/status")
def get_sync_status():
    """Get current sync progress. Poll during sync to see downloading track and progress."""
    from src.sync_state import get_state

    return get_state()


@app.get("/api/tracks", response_model=list[DownloadedTrack])
def list_downloaded_tracks(limit: int = 100):
    """List recently downloaded tracks."""
    from src.db import get_all_processed_tracks, init_db
    from src.playlist_store import get_playlists

    try:
        init_db()
        tracks = get_all_processed_tracks(limit=limit)
        playlists = {p["id"]: p.get("name", "Unknown") for p in get_playlists()}

        return [
            DownloadedTrack(
                video_id=t["video_id"],
                playlist_id=t["playlist_id"],
                playlist_name=playlists.get(t["playlist_id"], t["playlist_id"]),
                title=t["title"],
                artist=t["artist"],
                downloaded_at=t["downloaded_at"],
            )
            for t in tracks
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _run_sync_with_progress(playlist_id, result_holder):
    """Run sync in background, updating sync_state for progress."""
    from src.orchestrator import run
    from src.playlist_store import get_playlists
    from src.sync_state import set_current, set_running

    def progress_cb(video_id, title, artist, pl_id, pl_name, pct):
        from src.sync_state import update_progress

        if pct == 0:
            set_current(video_id, title, artist, pl_id, pl_name, 0)
        else:
            update_progress(pct)

    try:
        set_running(True)
        summary = run(playlist_id=playlist_id, progress_callback=progress_cb)
        playlists = {p["id"]: p.get("name", "Unknown") for p in get_playlists()}
        result_holder["result"] = {
            "success": True,
            "total_downloaded": sum(s["downloaded"] for s in summary.values()),
            "playlists": [
                {
                    "playlist_id": pl_id,
                    "playlist_name": playlists.get(pl_id, "Unknown"),
                    "new_count": s["new_count"],
                    "downloaded": s["downloaded"],
                    "failed": s["failed"],
                }
                for pl_id, s in summary.items()
            ],
        }
    except Exception as e:
        result_holder["result"] = {"success": False, "error": str(e)}
    finally:
        set_running(False)


@app.post("/api/sync", response_model=SyncResponse)
def trigger_sync(request: SyncRequest = SyncRequest()):
    """Trigger a sync. Runs in background; poll GET /api/sync/status for progress."""
    from src.sync_state import get_state

    state = get_state()
    if state.get("running"):
        raise HTTPException(status_code=409, detail="Sync already in progress")

    result_holder = {}
    thread = threading.Thread(
        target=_run_sync_with_progress,
        args=(request.playlist_id, result_holder),
    )
    thread.start()

    return SyncResponse(
        success=True,
        total_downloaded=0,
        playlists=[],
    )


# Serve built frontend (run `./run.sh` or `cd frontend && npm run build` first)
_frontend_dist = Path(__file__).parent / "frontend" / "dist"
if _frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=_frontend_dist / "assets"), name="assets")

    @app.get("/{path:path}")
    def serve_spa(path: str):
        """Serve index.html for SPA routing; static files for assets."""
        file_path = _frontend_dist / path
        if file_path.is_file():
            from fastapi.responses import FileResponse
            return FileResponse(file_path)
        return FileResponse(_frontend_dist / "index.html")
else:
    print("Note: frontend/dist not found. Build with: cd frontend && npm run build")
    print("Or use ./run.sh to build and start.")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
