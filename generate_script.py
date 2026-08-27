"""
generate_script.py
Fetches recent US finance/business headlines, then makes TWO SEPARATE,
smaller Gemini calls (one for the Short script, one for the Long script)
about the SAME topic - this keeps each request fast/reliable instead of
one huge slow request.
"""

import os
import json
import requests
import google.generativeai as genai

NEWS_API_KEY = os.environ["NEWS_API_KEY"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

genai.configure(api_key=GEMINI_API_KEY)

PILLAR = ("US personal and business finance news explained simply, and how "
          "it affects an ordinary person's wallet.")


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
    headlines = [
        f"- {a['title']}: {a.get('description') or ''}"
        for a in articles
        if a.get("title")
    ]
    return "\n".join(headlines[:15])


def call_gemini(prompt):
    model = genai.GenerativeModel("gemini-flash-latest")
    response = model.generate_content(prompt, request_options={"timeout": 180})
    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text)


def trim(scenes, max_words):
    for s in scenes:
        words = s["voiceover"].split()
        if len(words) > max_words:
            s["voiceover"] = " ".join(words[:max_words]) + "."


def generate():
    headlines = fetch_headlines()

    # --- CALL 1: pick the topic + write the SHORT script ---
    short_prompt = f"""You are a finance script writer for a channel called
MoneyPulse. Content pillar: {PILLAR} No AI avatar - text/graphics only.

Given today's real US finance headlines, pick the single best story (clearest
money impact, strongest hook), then write a 45-60 second Shorts script.

Return ONLY valid JSON, no markdown:
{{
  "topic": "the story, one sentence",
  "why_it_works": "1-2 sentences",
  "title": "punchy title under 60 chars",
  "description": "1-2 sentence description",
  "hashtags": ["#tag1","#tag2","#tag3","#tag4","#tag5"],
  "scenes": [
    {{"voiceover": "MAX 18 WORDS", "on_screen_text": "max 8 words", "footage_keyword": "1-3 words"}}
  ]
}}

Rules: exactly 6-8 scenes, each voiceover 18 words or fewer. Structure: hook,
problem, reality, hidden truth, example, advice, takeaway + comment trigger +
follow CTA. Use only real facts from headlines below. Casual, easy English.

Today's headlines:
{headlines}"""

    short_data = call_gemini(short_prompt)
    trim(short_data["scenes"], 18)

    # --- CALL 2: write the LONG script about the SAME topic ---
    long_prompt = f"""You are a finance script writer for a channel called
MoneyPulse. Content pillar: {PILLAR} No AI avatar - text/graphics only.

Write a 5-7 minute long-form video script about EXACTLY this story:
"{short_data['topic']}"

Go deeper than a short video: more context, background, examples, plain
English analysis of why it's happening and what happens next.

Return ONLY valid JSON, no markdown:
{{
  "title": "compelling title under 100 chars",
  "description": "3-4 sentence description",
  "hashtags": ["#tag1","#tag2","#tag3","#tag4","#tag5"],
  "scenes": [
    {{"voiceover": "MAX 30 WORDS", "on_screen_text": "max 8 words", "footage_keyword": "1-3 words"}}
  ]
}}

Rules: exactly 14-18 scenes, each voiceover 30 words or fewer. Structure:
hook, background, the news, why it's happening, historical context, who is
affected, multiple examples, analysis, what happens next, advice, takeaway +
comment trigger + follow CTA. Use only real facts, never invent numbers.
Casual, easy English."""

    long_data = call_gemini(long_prompt)
    trim(long_data["scenes"], 30)

    data = {
        "topic": short_data["topic"],
        "why_it_works": short_data["why_it_works"],
        "short": {
            "title": short_data["title"],
            "description": short_data["description"],
            "hashtags": short_data["hashtags"],
            "scenes": short_data["scenes"],
        },
        "long": {
            "title": long_data["title"],
            "description": long_data["description"],
            "hashtags": long_data["hashtags"],
            "scenes": long_data["scenes"],
        },
    }

    with open("today_script.json", "w") as f:
        json.dump(data, f, indent=2)

    print("Topic:", data["topic"])
    print("Short scenes:", len(data["short"]["scenes"]))
    print("Long scenes:", len(data["long"]["scenes"]))
    return data


if __name__ == "__main__":
    generate()
