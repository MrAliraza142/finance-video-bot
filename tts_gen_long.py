"""
tts_gen_long.py
Converts each LONG scene's voiceover into an mp3 using free Edge-TTS.
"""

import json
import asyncio
import edge_tts

VOICE = "en-US-AriaNeural"


async def make_audio(text, out_path):
    communicate = edge_tts.Communicate(text, VOICE, rate="+5%")
    await communicate.save(out_path)


def generate_all():
    with open("today_script_long.json") as f:
        data = json.load(f)
    for i, scene in enumerate(data["scenes"]):
        asyncio.run(make_audio(scene["voiceover"], f"audio_long_{i}.mp3"))
        print(f"Generated audio_long_{i}.mp3")


if __name__ == "__main__":
    generate_all()
