"""Playlist storage: Supabase (when configured) or config.yaml."""

import os
from typing import List, Optional


def _use_supabase() -> bool:
    """Check if Supabase is configured."""
    return bool(os.environ.get("SUPABASE_URL")
               and os.environ.get("SUPABASE_KEY"))


def _get_supabase():
    """Get Supabase client. Raises if not configured."""
    from supabase import create_client
    return create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_KEY"],
    )


def get_playlists() -> List[dict]:
    """Return list of playlists from Supabase or config."""
    if _use_supabase():
        try:
            sb = _get_supabase()
            r = sb.table("playlists").select("*").order("id").execute()
            return [{"id": row["id"], "name": row["name"], "paused": row.get("paused", False),
                    "thumbnail": row.get("thumbnail")} for row in (r.data or [])]
        except Exception as e:
            err = str(e)
            if "404" in err or "JSON could not be generated" in err:
                print("Supabase get_playlists error: Wrong SUPABASE_URL. Use Project URL from Supabase → Settings → API (e.g. https://xxx.supabase.co), NOT the dashboard URL.")
            else:
                print(f"Supabase get_playlists error: {e}")
            return []
    from .config import load_config, get_playlist_ids
    config = load_config()
    return get_playlist_ids(config)


def add_playlist(playlist_id: str, name: Optional[str] = None) -> dict:
    """Add a playlist. Uses Supabase if configured, else config.yaml."""
    if _use_supabase():
        from .config import _fetch_playlist_name, _fetch_playlist_thumbnail
        from .playlist_monitor import get_playlist_thumbnail
        if not name:
            name = _fetch_playlist_name(playlist_id)
        thumb = get_playlist_thumbnail(playlist_id)
        entry = {"id": playlist_id, "name": name or "Unknown Playlist", "paused": False}
        if thumb:
            entry["thumbnail"] = thumb
        try:
            sb = _get_supabase()
            sb.table("playlists").insert(entry).execute()
            return entry
        except Exception as e:
            err = str(e).lower()
            if "duplicate" in err or "unique" in err or "already exists" in err or "23505" in err:
                raise ValueError(f"Playlist {playlist_id} already in config")
            raise
    from .config import add_playlist as config_add
    return config_add(playlist_id, name)


def remove_playlist(playlist_id: str) -> None:
    """Remove a playlist."""
    if _use_supabase():
        try:
            sb = _get_supabase()
            r = sb.table("playlists").delete().eq("id", playlist_id).execute()
            if not r.data and not r.count:
                raise ValueError(f"Playlist {playlist_id} not found")
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Playlist {playlist_id} not found") from e
    else:
        from .config import remove_playlist as config_remove
        config_remove(playlist_id)


def set_playlist_paused(playlist_id: str, paused: bool) -> None:
    """Set paused state for a playlist."""
    if _use_supabase():
        try:
            sb = _get_supabase()
            r = sb.table("playlists").update({"paused": paused}).eq("id", playlist_id).execute()
            if not r.data:
                raise ValueError(f"Playlist {playlist_id} not found")
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Playlist {playlist_id} not found") from e
    else:
        from .config import set_playlist_paused as config_set
        config_set(playlist_id, paused)


def save_playlist_thumbnail(playlist_id: str, thumbnail: str) -> None:
    """Save thumbnail URL for a playlist."""
    if _use_supabase():
        try:
            sb = _get_supabase()
            sb.table("playlists").update({"thumbnail": thumbnail}).eq("id", playlist_id).execute()
        except Exception:
            pass
    else:
        from .config import save_playlist_thumbnail as config_save
        config_save(playlist_id, thumbnail)
