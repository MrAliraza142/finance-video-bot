"""
fetch_footage.py
Downloads one free vertical stock video clip per scene from Pexels
(free API, no cost) based on the footage_keyword generated for that scene.
Falls back to a generic finance clip if a search returns nothing.
"""

import os
import json
import requests

PEXELS_API_KEY = os.environ["PEXELS_API_KEY"]
HEADERS = {"Authorization": PEXELS_API_KEY}
FALLBACK_QUERY = "finance stock market"


def search_video(query):
    url = "https://api.pexels.com/videos/search"
    params = {"query": query, "orientation": "portrait", "size": "medium", "per_page": 5}
    r = requests.get(url, headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    videos = r.json().get("videos", [])
    if not videos:
        return None
    files = videos[0]["video_files"]
    vertical_files = [f for f in files if f.get("width", 0) < f.get("height", 1)]
    chosen = (vertical_files or files)[0]
    return chosen["link"]


def download(url, out_path):
    r = requests.get(url, stream=True, timeout=60)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)


def fetch_all():
    with open("today_script.json") as f:
        data = json.load(f)

    for i, scene in enumerate(data["scenes"]):
        query = scene.get("footage_keyword", FALLBACK_QUERY)
        link = search_video(query) or search_video(FALLBACK_QUERY)
        out_path = f"footage_scene_{i}.mp4"
        download(link, out_path)
        print(f"Downloaded footage for scene {i}: {query}")


if __name__ == "__main__":
    fetch_all()
