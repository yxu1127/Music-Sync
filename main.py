#!/usr/bin/env python3
"""YouTube Music Playlist Downloader - CLI entry point."""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Download new tracks from YouTube Music playlists as WAV files."
    )
    parser.add_argument(
        "--playlist",
        "-p",
        help="Process only this playlist ID (default: all playlists in config)",
    )
    parser.add_argument(
        "--test-auth",
        action="store_true",
        help="Test YouTube Music authentication and exit",
    )
    args = parser.parse_args()

    if args.test_auth:
        from src.config import get_playlist_ids, load_config
        from src.playlist_monitor import get_ytmusic
        try:
            yt = get_ytmusic()
            # Try get_library_playlists first (most reliable)
            try:
                lib_playlists = yt.get_library_playlists(limit=3)
                if lib_playlists:
                    names = [p.get("title", "?") for p in lib_playlists if p]
                    print(f"Auth OK! Your playlists: {names}")
                else:
                    raise ValueError("Empty response")
            except Exception:
                # Fallback: try get_playlist with config
                config = load_config()
                playlists = get_playlist_ids(config)
                if playlists:
                    pl = yt.get_playlist(playlists[0]["id"])
                    print(f"Auth OK! Fetched: {pl.get('title', 'playlist')}")
                else:
                    results = yt.search("test", filter="songs", limit=1)
                    print("Auth OK! (Search succeeded)")
        except Exception as e:
            err_str = str(e)
            if "logged_in" in err_str or "contents" in err_str or "NoneType" in err_str:
                print("Auth failed: Your browser session has expired or YouTube returned an unexpected response.")
                print("\nTo fix: Refresh your auth by getting new headers from YouTube Music:")
                print("  1. Open music.youtube.com in your browser (with ad blocker OFF)")
                print("  2. Make sure you're logged in")
                print("  3. Copy a 'browse' request headers → update headers.json")
                print("  4. Run: python convert_headers.py | ytmusicapi browser")
            else:
                print(f"Auth failed: {e}")
            sys.exit(1)
        return

    from src.orchestrator import run

    try:
        summary = run(playlist_id=args.playlist)
        total = sum(s["downloaded"] for s in summary.values())
        print(f"\nDone. Downloaded {total} track(s).")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
