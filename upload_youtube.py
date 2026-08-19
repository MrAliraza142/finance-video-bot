"""
upload_youtube.py
Uploads final_video.mp4 to YouTube as a Short using a pre-generated
OAuth refresh token (obtained once via Google's OAuth Playground; see
SETUP_GUIDE.md Part 3). The workflow uses it every day without needing
to log in again.
"""

import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

CLIENT_ID = os.environ["YT_CLIENT_ID"]
CLIENT_SECRET = os.environ["YT_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["YT_REFRESH_TOKEN"]


def get_authenticated_service():
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
    with open("today_script.json") as f:
        data = json.load(f)

    youtube = get_authenticated_service()

    title = data["title"]
    if "#Shorts" not in title:
        title = f"{title} #Shorts"

    description = data["description"] + "\n\n" + " ".join(data.get("hashtags", []))

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": [h.strip("#") for h in data.get("hashtags", [])],
            "categoryId": "25",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload("final_video.mp4", chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")

    print("Uploaded! Video ID:", response["id"])


if __name__ == "__main__":
    upload()
