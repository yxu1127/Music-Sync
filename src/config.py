"""Load and validate configuration from config.yaml and environment variables."""

import os
from pathlib import Path
from typing import List, Optional

import yaml


def _expand_path(path: str) -> Path:
    """Expand ~ and environment variables in path."""
    return Path(os.path.expanduser(os.path.expandvars(path)))


def load_config(config_path: Optional[str] = None) -> dict:
    """
    Load configuration from config.yaml.
    Merges with environment variables for secrets.
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config.yaml"

    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        config = yaml.safe_load(f)

    if not config:
        raise ValueError("Config file is empty")

    # Expand paths
    if "download" in config and "output_dir" in config["download"]:
        config["download"]["output_dir"] = str(
            _expand_path(config["download"]["output_dir"])
        )
    if "storage" in config and "local_path" in config["storage"]:
        config["storage"]["local_path"] = str(
            _expand_path(config["storage"]["local_path"])
        )

    # Load secrets from .env if present
    _load_env_secrets(config)

    # Render/cloud: COOKIES_BASE64 env writes cookies file for yt-dlp (no browser)
    _setup_cookies_file(config)

    return config


def _setup_cookies_file(config: dict) -> None:
    """If COOKIES_BASE64 env is set, decode and write to temp file for cloud hosting."""
    import base64
    import tempfile
    b64 = os.environ.get("COOKIES_BASE64", "").strip()
    if not b64:
        return
    try:
        content = base64.b64decode(b64).decode("utf-8")
        fd, path = tempfile.mkstemp(suffix=".txt", prefix="cookies_")
        with open(fd, "w") as f:
            f.write(content)
        config.setdefault("download", {})
        config["download"]["cookies_from_file"] = path
        config["download"]["cookies_browser"] = None  # Override browser
    except Exception as e:
        print(f"Warning: Failed to setup cookies from COOKIES_BASE64: {e}")


def setup_cloud_secrets() -> None:
    """Write Google credentials/token from env vars for Render/cloud hosting."""
    import base64
    project_root = Path(__file__).parent.parent
    for env_key, filename in [
        ("GOOGLE_CREDENTIALS_JSON", "credentials.json"),
        ("GOOGLE_TOKEN_JSON", "token_drive.json"),
    ]:
        raw = os.environ.get(env_key, "").strip()
        if not raw:
            continue
        try:
            content = base64.b64decode(raw).decode("utf-8")
        except Exception:
            content = raw  # Allow plain JSON for non-base64
        path = project_root / filename
        with open(path, "w") as f:
            f.write(content)


def _load_env_secrets(config: dict) -> None:
    """Load secrets from .env file into config (optional)."""
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        return

    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip("'\"")
                os.environ.setdefault(key, value)

    # Add auth section from env
    config.setdefault("auth", {})
    config["auth"]["ytmusic_client_id"] = os.environ.get("YTMUSIC_CLIENT_ID", "")
    config["auth"]["ytmusic_client_secret"] = os.environ.get(
        "YTMUSIC_CLIENT_SECRET", ""
    )


def get_playlist_ids(config: dict) -> List[dict]:
    """Return list of playlist configs: [{"id": "...", "name": "...", "paused": bool}, ...]."""
    return config.get("playlists", [])


def get_download_config(config: dict) -> dict:
    """Return download settings."""
    return config.get("download", {})


def get_storage_config(config: dict) -> dict:
    """Return storage settings."""
    return config.get("storage", {})


def set_schedule_interval(interval_minutes: int) -> None:
    """Update schedule interval in config.yaml. Valid range: 15–1440 minutes."""
    if interval_minutes < 15 or interval_minutes > 1440:
        raise ValueError("Interval must be between 15 and 1440 minutes")
    config_path = _get_config_path()
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path) as f:
        config = yaml.safe_load(f)
    config.setdefault("schedule", {})
    config["schedule"]["interval_minutes"] = interval_minutes
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def set_download_format(format: str) -> None:
    """Update download format in config.yaml. Valid: wav, mp3."""
    if format not in ("wav", "mp3"):
        raise ValueError("Format must be wav or mp3")
    config_path = _get_config_path()
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path) as f:
        config = yaml.safe_load(f)
    config.setdefault("download", {})
    config["download"]["format"] = format
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def _get_config_path() -> Path:
    """Return path to config.yaml."""
    return Path(__file__).parent.parent / "config.yaml"


def add_playlist(playlist_id: str, name: Optional[str] = None) -> dict:
    """
    Add a playlist to config.yaml. Fetches name from YouTube if not provided.
    Returns the added playlist dict. Raises ValueError if already exists.
    """
    config_path = _get_config_path()
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        config = yaml.safe_load(f)

    playlists = config.get("playlists", [])
    existing_ids = {p["id"] for p in playlists}
    if playlist_id in existing_ids:
        raise ValueError(f"Playlist {playlist_id} already in config")

    if not name:
        name = _fetch_playlist_name(playlist_id)

    thumbnail = _fetch_playlist_thumbnail(playlist_id)
    new_entry = {
        "id": playlist_id,
        "name": name or "Unknown Playlist",
        "paused": False,
        **({"thumbnail": thumbnail} if thumbnail else {}),
    }
    playlists.append(new_entry)
    config["playlists"] = playlists

    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    return new_entry


def remove_playlist(playlist_id: str) -> None:
    """Remove a playlist from config.yaml. Raises ValueError if not found."""
    config_path = _get_config_path()
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        config = yaml.safe_load(f)

    playlists = [p for p in config.get("playlists", []) if p["id"] != playlist_id]
    if len(playlists) == len(config.get("playlists", [])):
        raise ValueError(f"Playlist {playlist_id} not found")

    config["playlists"] = playlists
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def set_playlist_paused(playlist_id: str, paused: bool) -> None:
    """Set paused state for a playlist. Updates config.yaml."""
    config_path = _get_config_path()
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        config = yaml.safe_load(f)

    playlists = config.get("playlists", [])
    found = False
    for p in playlists:
        if p["id"] == playlist_id:
            p["paused"] = paused
            found = True
            break
    if not found:
        raise ValueError(f"Playlist {playlist_id} not found")

    config["playlists"] = playlists
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def save_playlist_thumbnail(playlist_id: str, thumbnail: str) -> None:
    """Save thumbnail URL to config for a playlist."""
    config_path = _get_config_path()
    if not config_path.exists():
        return
    with open(config_path) as f:
        config = yaml.safe_load(f)
    for p in config.get("playlists", []):
        if p["id"] == playlist_id:
            p["thumbnail"] = thumbnail
            break
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def _fetch_playlist_thumbnail(playlist_id: str) -> Optional[str]:
    """Fetch playlist thumbnail URL from YouTube."""
    from .playlist_monitor import get_playlist_thumbnail
    return get_playlist_thumbnail(playlist_id)


def _fetch_playlist_name(playlist_id: str) -> str:
    """Fetch playlist title from YouTube via yt-dlp."""
    import yt_dlp

    url = f"https://www.youtube.com/playlist?list={playlist_id}"
    try:
        with yt_dlp.YoutubeDL({"quiet": True, "extract_flat": True}) as ydl:
            info = ydl.extract_info(url, download=False)
            return (info or {}).get("title") or "Unknown Playlist"
    except Exception:
        return "Unknown Playlist"
