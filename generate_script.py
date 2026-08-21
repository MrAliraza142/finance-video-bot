"""
generate_script.py
Fetches recent US finance/business headlines (free NewsAPI.org tier),
then uses Google Gemini (free tier) to generate a viral finance script
following the Hook -> Body -> Ending template, for either a Short
(45-60s) or a Long-form (8-10 min) video.

Output: writes today_script.json used by later steps.
"""

import os
import json
import requests
import google.generativeai as genai

NEWS_API_KEY = os.environ["NEWS_API_KEY"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
VIDEO_LENGTH = os.environ.get("VIDEO_LENGTH", "short")  # "short" or "long"

genai.configure(api_key=GEMINI_API_KEY)


def fetch_headlines():
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "country": "us",
        "category": "business",
        "pageSize": 20,
        "apiKey": NEWS_API_KEY,
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    articles = r.json().get("articles", [])
    headlines = [
        f"- {a['title']}: {a.get('description') or ''}"
        for a in articles
        if a.get("title")
    ]
    return "\n".join(headlines[:20])


def build_prompt(headlines):
    if VIDEO_LENGTH == "long":
        length_rules = """
- Create 16 to 22 scenes total, each scene's voiceover should be 25-40 seconds
  of spoken content, for a TOTAL video length of 8 to 10 minutes.
- This is a long-form YouTube video, not a Short. Go deep: include more
  context, more than one supporting fact/statistic per section, and a
  fuller worked example.
"""
        format_note = "long-form YouTube video (8-10 minutes)"
    else:
        length_rules = """
- Create 6 to 8 scenes total, each scene's voiceover should be 6-9 seconds
  of spoken content, for a TOTAL video length of 45-60 seconds.
"""
        format_note = "short vertical video for YouTube Shorts / TikTok (45-60 seconds)"

    return f"""You are a Senior Finance Researcher, Content Strategist, and Viral
Script Writer for a faceless finance channel aimed at a US audience. No AI
avatar/character is used - videos are text/graphics/chart-based only.

Given today's real US finance/business headlines below, first do a quick
internal analysis of which topic has the best mix of viral potential,
entertainment value, finance value, and US relevancy - then write a
{format_note} script for the single best topic, following this exact
structure:

HOOK (first scene): A shocking or emotional line that stops someone from
scrolling. No boring intros.

BODY (middle scenes, in this order): Problem -> Reality -> Hidden Truth ->
an interesting fact -> a simple relatable example -> one piece of
actionable advice. Each part should flow naturally into the next.

ENDING (last scene): A strong one-line takeaway, then a comment-trigger
question, then a "follow for tomorrow" call to action.

Tone: casual, friendly, smart, conversational - never robotic. Easy
everyday English, avoid jargon unless briefly explained. Only use
verified, real numbers/facts from the headlines provided - never invent
statistics.

Return ONLY valid JSON, no markdown, no explanation, in this exact shape:

{{
  "topic": "the single best topic for today, one clear sentence",
  "why_it_works": "1-2 sentences on why this will perform well",
  "title": "punchy video title, under 60 characters",
  "description": "1-2 sentence YouTube/TikTok description",
  "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
  "scenes": [
    {{
      "voiceover": "the exact line(s) the narrator says in this scene",
      "on_screen_text": "short punchy caption text for this scene (max 8 words)",
      "footage_keyword": "1-3 word search term for free stock footage that fits this scene"
    }}
  ]
}}

Rules:
{length_rules}
- Use only verified, real numbers/facts from the provided headlines.
- Last scene must include a comment-trigger question and a "follow for
  tomorrow" call to action.

Today's real US finance headlines:
{headlines}
"""


def generate():
    headlines = fetch_headlines()
    model = genai.GenerativeModel("gemini-flash-latest")
    prompt = build_prompt(headlines)
    response = model.generate_content(prompt)

    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    data = json.loads(text)
    data["video_length"] = VIDEO_LENGTH

    with open("today_script.json", "w") as f:
        json.dump(data, f, indent=2)

    print(f"Script generated ({VIDEO_LENGTH}):", data["title"])
    return data


if __name__ == "__main__":
    generate()
