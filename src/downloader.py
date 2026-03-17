"""Download YouTube audio and convert to WAV using yt-dlp."""

import re
import shutil
from pathlib import Path
from typing import Callable, Optional

import yt_dlp


def _sanitize_filename(name: str) -> str:
    """Remove characters that are invalid in filenames."""
    # Replace invalid chars with underscore
    sanitized = re.sub(r'[<>:"/\\|?*]', "_", name)
    # Limit length
    return sanitized[:200].strip() or "unknown"


def download_track(
    video_id: str,
    output_dir: str,
    format: str = "wav",
    quality: str = "0",
    title: Optional[str] = None,
    artist: Optional[str] = None,
    cookies_browser: Optional[str] = None,
    cookies_from_file: Optional[str] = None,
    progress_callback: Optional[Callable[[float], None]] = None,
) -> Optional[str]:
    """
    Download a YouTube track and convert to audio format.
    Returns path to the downloaded file, or None on failure.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build output template: Artist - Title.ext (or just Title.ext)
    if artist and title:
        out_tmpl = str(output_dir / f"{_sanitize_filename(artist)} - {_sanitize_filename(title)}.%(ext)s")
    elif title:
        out_tmpl = str(output_dir / f"{_sanitize_filename(title)}.%(ext)s")
    else:
        out_tmpl = str(output_dir / f"%(title)s.%(ext)s")

    def _progress_hook(d):
        if not progress_callback or d.get("status") != "downloading":
            return
        total = d.get("total_bytes") or d.get("total_bytes_estimate")
        downloaded = d.get("downloaded_bytes", 0)
        frag_idx = d.get("fragment_index")
        frag_count = d.get("fragment_count")
        if total and total > 0:
            progress_callback(min(100, 100 * downloaded / total))
        elif frag_count and frag_count > 0 and frag_idx is not None:
            progress_callback(min(100, 100 * (frag_idx + 1) / frag_count))
        else:
            progress_callback(0)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": out_tmpl,
        "quiet": False,
        "no_warnings": False,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": format,
                "preferredquality": quality,
            }
        ],
    }
    if progress_callback:
        ydl_opts["progress_hooks"] = [_progress_hook]
    # Cookies for YouTube auth (browser or file for cloud hosting)
    if cookies_from_file and Path(cookies_from_file).exists():
        ydl_opts["cookiefile"] = cookies_from_file
    elif cookies_browser:
        ydl_opts["cookiesfrombrowser"] = (cookies_browser,)

    # Use Node.js for YouTube signature solving (Deno is default but may not be installed)
    node_path = shutil.which("node")
    if node_path:
        ydl_opts["js_runtimes"] = {"node": {"path": node_path}}

    url = f"https://www.youtube.com/watch?v={video_id}"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                return None

            # Find the output file (yt-dlp adds the extension)
            base = Path(ydl.prepare_filename(info))
            # After FFmpegExtractAudio, extension changes to format
            audio_file = base.with_suffix(f".{format}")
            if audio_file.exists():
                return str(audio_file)

            # Fallback: look for any file with this base name
            for f in output_dir.glob(f"{base.stem}.*"):
                return str(f)

            return None

    except Exception as e:
        print(f"Download failed for {video_id}: {e}")
        return None
