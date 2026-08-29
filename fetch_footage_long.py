"""
fetch_footage_long.py
Downloads one free landscape stock video clip per LONG scene from Pexels.
"""

import os
import json
import requests

PEXELS_API_KEY = os.environ["PEXELS_API_KEY"]
HEADERS = {"Authorization": PEXELS_API_KEY}
FALLBACK_QUERY = "finance stock market"


def search_video(query):
    url = "https://api.pexels.com/videos/search"
    params = {"query": query, "orientation": "landscape", "size": "medium", "per_page": 5}
    r = requests.get(url, headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    videos = r.json().get("videos", [])
    if not videos:
        return None
    files = videos[0]["video_files"]
    landscape = [f for f in files if f.get("width", 0) > f.get("height", 1)]
    return (landscape or files)[0]["link"]


def download(url, out_path):
    r = requests.get(url, stream=True, timeout=60)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)


def fetch_all():
    with open("today_script_long.json") as f:
        data = json.load(f)
    for i, scene in enumerate(data["scenes"]):
        query = scene.get("footage_keyword", FALLBACK_QUERY)
        link = search_video(query) or search_video(FALLBACK_QUERY)
        download(link, f"footage_long_{i}.mp4")
        print(f"Downloaded footage_long_{i}.mp4: {query}")


if __name__ == "__main__":
    fetch_all()
