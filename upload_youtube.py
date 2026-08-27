"""
upload_youtube.py
Uploads BOTH final_video_short.mp4 (as a YouTube Short) and
final_video_long.mp4 (as a regular long-form video).
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


def upload_one(youtube, video_path, title, description, hashtags, is_short):
    if is_short and "#Shorts" not in title:
        title = f"{title} #Shorts"

    full_description = description + "\n\n" + " ".join(hashtags)

    body = {
        "snippet": {
            "title": title[:100],
            "description": full_description,
            "tags": [h.strip("#") for h in hashtags],
            "categoryId": "25",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  Upload progress: {int(status.progress() * 100)}%")

    print(f"Uploaded! Video ID: {response['id']}")
    return response["id"]


def upload():
    with open("today_script.json") as f:
        data = json.load(f)

    youtube = get_authenticated_service()

    print("Uploading SHORT...")
    upload_one(
        youtube, "final_video_short.mp4",
        data["short"]["title"], data["short"]["description"],
        data["short"].get("hashtags", []), is_short=True,
    )

    print("Uploading LONG...")
    upload_one(
        youtube, "final_video_long.mp4",
        data["long"]["title"], data["long"]["description"],
        data["long"].get("hashtags", []), is_short=False,
    )


if __name__ == "__main__":
    upload()
