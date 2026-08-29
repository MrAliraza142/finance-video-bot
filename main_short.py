"""
main_short.py
Runs the full SHORT pipeline: script -> voice -> footage -> assemble -> upload.
"""

import generate_script_short
import tts_gen_short
import fetch_footage_short
import assemble_video_short
import upload_youtube_short

if __name__ == "__main__":
    print("=== SHORT STEP 1: Script ===")
    generate_script_short.generate()
    print("=== SHORT STEP 2: Voiceover ===")
    tts_gen_short.generate_all()
    print("=== SHORT STEP 3: Footage ===")
    fetch_footage_short.fetch_all()
    print("=== SHORT STEP 4: Assemble ===")
    assemble_video_short.assemble()
    print("=== SHORT STEP 5: Upload ===")
    upload_youtube_short.upload()
    print("=== SHORT DONE ===")
