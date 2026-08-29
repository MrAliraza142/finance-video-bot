"""
upload_youtube_long.py
Uploads final_video_long.mp4 as a regular (non-Shorts) YouTube video.
"""

import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

CLIENT_ID = os.environ["YT_CLIENT_ID"]
CLIENT_SECRET = os.environ["YT_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["YT_REFRESH_TOKEN"]


def get_service():
    creds = Credentials(
        token=None,
        refresh_token=REFRESH_TOKEN,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )
    return build("youtube", "v3", credentials=creds)


def upload():
    with open("today_script_long.json") as f:
        data = json.load(f)

    youtube = get_service()
    description = data["description"] + "\n\n" + " ".join(data.get("hashtags", []))

    body = {
        "snippet": {
            "title": data["title"][:100],
            "description": description,
            "tags": [h.strip("#") for h in data.get("hashtags", [])],
            "categoryId": "25",
        },
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
    }
    media = MediaFileUpload("final_video_long.mp4", chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")
    print("Uploaded LONG! Video ID:", response["id"])


if __name__ == "__main__":
    upload()
