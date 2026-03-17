"""Monitor YouTube Music playlists for new tracks."""

from pathlib import Path
from typing import List, Optional

import yt_dlp

from . import db


def get_playlist_thumbnail(playlist_id: str) -> Optional[str]:
    """Fetch playlist thumbnail URL from YouTube. Returns None on failure."""
    url = f"https://www.youtube.com/playlist?list={playlist_id}"
    ydl_opts = {"quiet": True, "extract_flat": True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return None
            thumb = info.get("thumbnail")
            if thumb:
                return thumb
            thumbs = info.get("thumbnails")
            if thumbs:
                best = thumbs[-1] if isinstance(thumbs[-1], dict) else thumbs[0]
                return best.get("url") if isinstance(best, dict) else None
            entries = info.get("entries") or []
            first = next((e for e in entries if e), None)
            if first and isinstance(first, dict):
                vid = first.get("id")
                if vid:
                    return f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
                return first.get("thumbnail")
            return None
    except Exception:
        return None


def get_ytmusic():
    """Return YTMusic client if auth exists (for test-auth). Playlist fetch uses yt-dlp."""
    from ytmusicapi import YTMusic
    project_root = Path(__file__).parent.parent
    for name in ("browser.json", "oauth.json"):
        path = project_root / name
        if path.exists():
            return YTMusic(str(path))
    raise FileNotFoundError("No auth file. Run 'ytmusicapi browser' first.")


def get_new_tracks(playlist_id: str) -> List[dict]:
    """
    Fetch playlist via yt-dlp (bypasses broken ytmusicapi get_playlist).
    Returns list of dicts with: videoId, title, artist
    """
    db.init_db()
    processed_ids = set(db.get_processed_ids(playlist_id))

    url = f"https://www.youtube.com/playlist?list={playlist_id}"
    ydl_opts = {
        "quiet": True,
        "extract_flat": False,
        "extract_info": True,
    }

    new_tracks = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info or "entries" not in info:
                return []

            for entry in info["entries"]:
                if not entry:
                    continue
                video_id = entry.get("id")
                if not video_id or video_id in processed_ids:
                    continue

                title = entry.get("title") or entry.get("track") or "Unknown"
                artist = entry.get("artist") or entry.get("uploader") or ""

                new_tracks.append({
                    "videoId": video_id,
                    "title": title,
                    "artist": artist,
                })
    except Exception:
        return []

    return new_tracks
