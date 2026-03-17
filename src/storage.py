"""Local file storage for downloaded tracks."""

import shutil
from pathlib import Path
from typing import Optional


def save_locally(
    source_path: str,
    output_dir: str,
    subfolder: Optional[str] = None,
) -> str:
    """
    Save/copy a file to the local storage directory.
    Optionally organize in a subfolder (e.g. by playlist name).
    Returns the final destination path.
    """
    output_dir = Path(output_dir)
    if subfolder:
        output_dir = output_dir / subfolder
    output_dir.mkdir(parents=True, exist_ok=True)

    source = Path(source_path)
    dest = output_dir / source.name

    if source != dest:
        shutil.copy2(source, dest)

    return str(dest)


def ensure_output_dir(path: str) -> Path:
    """Create output directory if it doesn't exist."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
