"""Shared state for sync progress (used by API and orchestrator)."""

_sync_state = {
    "running": False,
    "current": None,  # {video_id, title, artist, playlist_id, playlist_name, progress}
}


def get_state():
    return _sync_state.copy()


def set_running(running: bool):
    _sync_state["running"] = running
    if not running:
        _sync_state["current"] = None


def set_current(video_id: str, title: str, artist: str, playlist_id: str, playlist_name: str, progress: float = 0):
    _sync_state["current"] = {
        "video_id": video_id,
        "title": title,
        "artist": artist,
        "playlist_id": playlist_id,
        "playlist_name": playlist_name,
        "progress": progress,
    }


def update_progress(progress: float):
    if _sync_state["current"] is not None:
        _sync_state["current"]["progress"] = progress
