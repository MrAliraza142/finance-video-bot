"""
generate_script_short.py
Trend-research + viral script generation for the SHORT (YouTube Shorts)
pipeline. Runs independently from the long-form pipeline so a failure or
slowness in one never affects the other.
"""

import os
import json
import time
import requests
import google.generativeai as genai

NEWS_API_KEY = os.environ["NEWS_API_KEY"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

genai.configure(api_key=GEMINI_API_KEY)


def fetch_headlines():
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "country": "us",
        "category": "business",
        "pageSize": 15,
        "apiKey": NEWS_API_KEY,
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    articles = r.json().get("articles", [])
    return "\n".join(
        f"- {a['title']}: {a.get('description') or ''}"
        for a in articles if a.get("title")
    )[:6000]


PROMPT = """You are a Senior Finance Trend Research Analyst AND viral TikTok/
Shorts script writer for a US finance channel called MoneyPulse.

STEP 1 - TREND RESEARCH: Look at today's real US finance/business headlines
below. Mentally score the top candidate stories on: Viral Score, Entertainment
Score, Finance Value, US Relevancy, Audience Curiosity. Pick the single best
"Topic of Today" - the one most likely to stop someone scrolling and go viral.

STEP 2 - SCRIPT: Write a 45-60 second Shorts script for that topic.
Tone: casual, friendly, entertaining, smart, not robotic.
Structure: HOOK (shocking/emotional, 0-3 sec) -> BODY (problem -> reality ->
hidden truth -> simple example -> actionable advice) -> ENDING (strong
takeaway -> comment-trigger question -> follow CTA).
Use only verified, real numbers from the headlines - never invent stats.
Easy English, avoid jargon, natural flow, end in a way that makes people want
"part 2" tomorrow.

Return ONLY valid JSON, no markdown:
{
  "topic": "one sentence",
  "why_it_works": "1-2 sentences",
  "title": "punchy title under 60 chars",
  "description": "1-2 sentence description",
  "hashtags": ["#tag1","#tag2","#tag3","#tag4","#tag5"],
  "scenes": [
    {"voiceover": "MAX 18 WORDS", "on_screen_text": "max 8 words", "footage_keyword": "1-3 words"}
  ]
}
Rules: exactly 6-8 scenes, each voiceover 18 words or FEWER (count before
finalizing).

Today's real US finance headlines:
"""


def call_gemini_with_retry(prompt, attempts=3):
    model = genai.GenerativeModel("gemini-flash-latest")
    last_err = None
    for i in range(attempts):
        try:
            response = model.generate_content(prompt, request_options={"timeout": 180})
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text)
        except Exception as e:
            last_err = e
            print(f"Gemini attempt {i+1} failed: {e}")
            time.sleep(10)
    raise last_err


def generate():
    headlines = fetch_headlines()
    data = call_gemini_with_retry(PROMPT + headlines)

    for s in data["scenes"]:
        words = s["voiceover"].split()
        if len(words) > 18:
            s["voiceover"] = " ".join(words[:18]) + "."

    with open("today_script_short.json", "w") as f:
        json.dump(data, f, indent=2)

    print("SHORT topic:", data["topic"])
    print("Scenes:", len(data["scenes"]))
    return data


if __name__ == "__main__":
    generate()
