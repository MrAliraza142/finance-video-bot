"""
tts_gen.py
Converts each scene's voiceover text into an mp3 file using free Edge-TTS
(Microsoft's free text-to-speech, no API key needed).
Produces one audio file per scene so we know exact per-scene duration
for syncing captions/footage later.
"""

import json
import asyncio
import edge_tts

VOICE = "en-US-AriaNeural"  # free natural US female voice; try en-US-GuyNeural for male


async def make_audio(text, out_path):
    communicate = edge_tts.Communicate(text, VOICE, rate="+5%")
    await communicate.save(out_path)


def generate_all():
    with open("today_script.json") as f:
        data = json.load(f)

    for i, scene in enumerate(data["scenes"]):
        out_path = f"audio_scene_{i}.mp3"
        asyncio.run(make_audio(scene["voiceover"], out_path))
        print(f"Generated {out_path}")


if __name__ == "__main__":
    generate_all()
