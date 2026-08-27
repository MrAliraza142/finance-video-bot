"""
tts_gen.py
Converts each scene's voiceover text (for BOTH the short and long script)
into mp3 files using free Edge-TTS.
"""

import json
import asyncio
import edge_tts

VOICE = "en-US-AriaNeural"


async def make_audio(text, out_path):
    communicate = edge_tts.Communicate(text, VOICE, rate="+5%")
    await communicate.save(out_path)


def generate_all():
    with open("today_script.json") as f:
        data = json.load(f)

    for i, scene in enumerate(data["short"]["scenes"]):
        asyncio.run(make_audio(scene["voiceover"], f"audio_short_{i}.mp3"))
        print(f"Generated audio_short_{i}.mp3")

    for i, scene in enumerate(data["long"]["scenes"]):
        asyncio.run(make_audio(scene["voiceover"], f"audio_long_{i}.mp3"))
        print(f"Generated audio_long_{i}.mp3")


if __name__ == "__main__":
    generate_all()
