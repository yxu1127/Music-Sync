"""Orchestrate the full pipeline: monitor -> download -> store -> mark processed."""

from pathlib import Path
from typing import Callable, List, Optional

from . import db
from .config import get_download_config, get_storage_config, load_config
from .playlist_store import get_playlists
from .downloader import download_track
from .drive_uploader import get_drive_service, ensure_folder, upload_file
from .playlist_monitor import get_new_tracks
from .storage import save_locally


def run(playlist_id: Optional[str] = None, progress_callback: Optional[Callable] = None) -> dict:
    """
    Run the full pipeline for one or all playlists.
    If playlist_id is given, only process that playlist.
    Returns summary: {playlist_id: {downloaded: N, failed: N, new_count: N}}
    """
    config = load_config()
    db.init_db()

    playlists = get_playlists()
    if playlist_id:
        playlists = [p for p in playlists if p["id"] == playlist_id]
        if not playlists:
            raise ValueError(f"Playlist {playlist_id} not found in config")
    else:
        playlists = [p for p in playlists if not p.get("paused", False)]

    download_cfg = get_download_config(config)
    storage_cfg = get_storage_config(config)

    output_dir = download_cfg.get("output_dir", "./downloads")
    audio_format = download_cfg.get("format", "wav")
    quality = download_cfg.get("quality", "0")
    cookies_browser = download_cfg.get("cookies_browser")
    cookies_from_file = download_cfg.get("cookies_from_file")

    local_path = storage_cfg.get("local_path", output_dir)
    use_local = storage_cfg.get("local", True)
    use_drive = storage_cfg.get("google_drive", False)
    drive_folder_id = storage_cfg.get("drive_folder_id") or ""

    # Initialize Drive service if needed
    drive_service = None
    if use_drive:
        try:
            drive_service = get_drive_service()
        except Exception as e:
            print(f"Warning: Google Drive auth failed: {e}. Skipping Drive upload.")
            use_drive = False

    summary = {}

    for pl in playlists:
        pl_id = pl["id"]
        pl_name = pl.get("name", "Unknown")

        new_tracks = get_new_tracks(pl_id)
        summary[pl_id] = {"new_count": len(new_tracks), "downloaded": 0, "failed": 0}

        if not new_tracks:
            print(f"[{pl_name}] No new tracks.")
            continue

        print(f"[{pl_name}] Found {len(new_tracks)} new track(s).")

        subfolder = _sanitize_folder(pl_name) if use_local else None

        for track in new_tracks:
            video_id = track["videoId"]
            title = track.get("title", "Unknown")
            artist = track.get("artist", "")

            print(f"  Downloading: {artist} - {title}" if artist else f"  Downloading: {title}")

            def _progress(pct):
                if progress_callback:
                    progress_callback(video_id, title, artist, pl_id, pl_name, pct)

            if progress_callback:
                progress_callback(video_id, title, artist, pl_id, pl_name, 0)

            file_path = download_track(
                video_id=video_id,
                output_dir=output_dir,
                format=audio_format,
                quality=quality,
                title=title,
                artist=artist,
                cookies_browser=cookies_browser,
                cookies_from_file=cookies_from_file,
                progress_callback=_progress if progress_callback else None,
            )

            if file_path:
                if use_local and local_path != output_dir:
                    file_path = save_locally(file_path, local_path, subfolder=subfolder)
                if use_drive and drive_service:
                    # drive_folder_id: upload to this folder, or create "YouTube Music/PlaylistName" at root
                    base_folder_id = drive_folder_id.strip() if drive_folder_id else None
                    if base_folder_id:
                        pl_folder_id = ensure_folder(
                            drive_service, _sanitize_folder(pl_name), parent_id=base_folder_id
                        )
                    else:
                        root_folder = ensure_folder(drive_service, "YouTube Music")
                        pl_folder_id = ensure_folder(
                            drive_service, _sanitize_folder(pl_name), parent_id=root_folder
                        )
                    if upload_file(drive_service, file_path, folder_id=pl_folder_id):
                        print(f"    -> Uploaded to Drive")
                    else:
                        print(f"    -> Drive upload failed")
                db.mark_processed(video_id, pl_id, title=title, artist=artist)
                summary[pl_id]["downloaded"] += 1
                print(f"    -> Saved: {file_path}")
            else:
                summary[pl_id]["failed"] += 1
                print(f"    -> Failed")

    return summary


def _sanitize_folder(name: str) -> str:
    """Sanitize playlist name for use as folder name."""
    import re
    return re.sub(r'[<>:"/\\|?*]', "_", name)[:100].strip() or "Playlist"
