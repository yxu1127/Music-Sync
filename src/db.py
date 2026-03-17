"""SQLite database for tracking processed tracks."""

import sqlite3
from pathlib import Path
from typing import List, Optional


def _get_db_path() -> Path:
    """Return path to the state database."""
    return Path(__file__).parent.parent / "state.db"


def init_db() -> None:
    """Create database and tables if they don't exist."""
    db_path = _get_db_path()
    conn = sqlite3.connect(str(db_path))
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS processed_tracks (
            video_id TEXT NOT NULL,
            playlist_id TEXT NOT NULL,
            title TEXT,
            artist TEXT,
            downloaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (video_id, playlist_id)
        );
        CREATE INDEX IF NOT EXISTS idx_processed_playlist
            ON processed_tracks(playlist_id);
    """)
    conn.commit()
    conn.close()


def is_processed(video_id: str, playlist_id: str) -> bool:
    """Check if a track has already been processed."""
    conn = sqlite3.connect(str(_get_db_path()))
    cursor = conn.execute(
        "SELECT 1 FROM processed_tracks WHERE video_id = ? AND playlist_id = ?",
        (video_id, playlist_id),
    )
    result = cursor.fetchone() is not None
    conn.close()
    return result


def mark_processed(
    video_id: str,
    playlist_id: str,
    title: Optional[str] = None,
    artist: Optional[str] = None,
) -> None:
    """Mark a track as processed."""
    conn = sqlite3.connect(str(_get_db_path()))
    conn.execute(
        """
        INSERT OR REPLACE INTO processed_tracks (video_id, playlist_id, title, artist)
        VALUES (?, ?, ?, ?)
        """,
        (video_id, playlist_id, title or "", artist or ""),
    )
    conn.commit()
    conn.close()


def get_processed_ids(playlist_id: str) -> List[str]:
    """Return list of video IDs already processed for a playlist."""
    conn = sqlite3.connect(str(_get_db_path()))
    cursor = conn.execute(
        "SELECT video_id FROM processed_tracks WHERE playlist_id = ?",
        (playlist_id,),
    )
    ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return ids


def get_all_processed_tracks(limit: int = 100) -> List[dict]:
    """Return recently downloaded tracks: video_id, playlist_id, title, artist, downloaded_at."""
    conn = sqlite3.connect(str(_get_db_path()))
    cursor = conn.execute(
        """
        SELECT video_id, playlist_id, title, artist, downloaded_at
        FROM processed_tracks
        ORDER BY downloaded_at DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "video_id": r[0],
            "playlist_id": r[1],
            "title": r[2] or "Unknown",
            "artist": r[3] or "",
            "downloaded_at": r[4],
        }
        for r in rows
    ]
