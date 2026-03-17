#!/usr/bin/env python3
"""Diagnostic script to debug auth issues."""

import json
from pathlib import Path

def main():
    project = Path(__file__).parent
    browser_json = project / "browser.json"
    headers_json = project / "headers.json"

    print("=== Auth Diagnostic ===\n")

    # Check browser.json
    if browser_json.exists():
        with open(browser_json) as f:
            data = json.load(f)
        has_auth = "authorization" in data or "Authorization" in data
        has_cookie = "cookie" in data or "Cookie" in data
        has_xgoog = "x-goog-authuser" in data or "X-Goog-AuthUser" in data
        print(f"browser.json: EXISTS")
        print(f"  - Authorization: {'YES' if has_auth else 'MISSING'}")
        print(f"  - Cookie: {'YES' if has_cookie else 'MISSING'}")
        print(f"  - X-Goog-AuthUser: {'YES' if has_xgoog else 'MISSING'}")
    else:
        print("browser.json: MISSING (run: python convert_headers.py | ytmusicapi browser)")

    # Check headers.json
    if headers_json.exists():
        with open(headers_json) as f:
            data = json.load(f)
        has_auth = "authorization" in data or "Authorization" in data
        has_cookie = "cookie" in data or "Cookie" in data
        print(f"\nheaders.json: EXISTS")
        print(f"  - Authorization: {'YES' if has_auth else 'MISSING'}")
        print(f"  - Cookie: {'YES' if has_cookie else 'MISSING'}")
    else:
        print("\nheaders.json: MISSING")

    # Try actual API call
    print("\n--- Testing API ---")
    try:
        from ytmusicapi import YTMusic
        yt = YTMusic(str(browser_json))
        playlists = yt.get_library_playlists(limit=2)
        if playlists:
            print(f"SUCCESS! Got {len(playlists)} playlist(s): {[p.get('title') for p in playlists]}")
        else:
            print("API returned empty list (auth may be expired)")
    except Exception as e:
        print(f"FAILED: {e}")
        print("\nIf you see 'logged_in' or 'contents' - your session expired.")
        print("Get fresh headers from music.youtube.com (DevTools → Network → browse request)")

if __name__ == "__main__":
    main()
