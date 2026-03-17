#!/usr/bin/env python3
"""Convert headers.json to the format ytmusicapi browser expects (key: value per line)."""
import json
import sys

with open("headers.json") as f:
    headers = json.load(f)

for key, value in headers.items():
    print(f"{key}: {value}")
