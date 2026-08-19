"""
main.py
Runs the full daily pipeline in order. This is what GitHub Actions
calls every day automatically:
  1. Generate topic + script (Gemini + real headlines)
  2. Generate voiceover audio (Edge-TTS, free)
  3. Fetch matching stock footage (Pexels, free)
  4. Assemble final vertical video (MoviePy/FFmpeg, free)
  5. Upload to YouTube as a Short
"""

import generate_script
import tts_gen
import fetch_footage
import assemble_video
import upload_youtube

if __name__ == "__main__":
    print("=== STEP 1: Generating script ===")
    generate_script.generate()

    print("=== STEP 2: Generating voiceover ===")
    tts_gen.generate_all()

    print("=== STEP 3: Fetching footage ===")
    fetch_footage.fetch_all()

    print("=== STEP 4: Assembling video ===")
    assemble_video.assemble()

    print("=== STEP 5: Uploading to YouTube ===")
    upload_youtube.upload()

    print("=== DONE. Today's video is live. ===")
