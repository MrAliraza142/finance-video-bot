"""
upload_youtube_short.py
Uploads final_video_short.mp4 as a YouTube Short.
"""

import os
import sys
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# .strip() hata deta hai accidental spaces/newlines jo copy-paste karte waqt
# GitHub Secrets mein chale jate hain (ye humari history mein 3+ baar error ki wajah bana)
CLIENT_ID = os.environ["YT_CLIENT_ID"].strip()
CLIENT_SECRET = os.environ["YT_CLIENT_SECRET"].strip()
REFRESH_TOKEN = os.environ["YT_REFRESH_TOKEN"].strip()


def get_service():
    creds = Credentials(
        token=None,
        refresh_token=REFRESH_TOKEN,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )

    # Yahan turant refresh try karte hain, video processing shuru karne se PEHLE.
    # Agar token invalid hai to yahin fail hoga, 3-4 minute video encoding waste
    # nahi hogi, aur error message bhi clear hoga.
    try:
        creds.refresh(Request())
    except RefreshError as e:
        print("=" * 60)
        print("YOUTUBE AUTH FAILED — Refresh token invalid/expired/revoked.")
        print("Fix: naya Client ID + Secret + Refresh Token EK HI SESSION")
        print("mein generate karein aur GitHub Secrets update karein.")
        print(f"Original error: {e}")
        print("=" * 60)
        sys.exit(1)

    return build("youtube", "v3", credentials=creds)


def upload():
    with open("today_script_short.json") as f:
        data = json.load(f)

    youtube = get_service()
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
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
    }
    media = MediaFileUpload("final_video_short.mp4", chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")
    print("Uploaded SHORT! Video ID:", response["id"])


if __name__ == "__main__":
    upload()
