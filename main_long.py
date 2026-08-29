"""
main_long.py
Runs the full LONG pipeline: script -> voice -> footage -> assemble -> upload.
"""

import generate_script_long
import tts_gen_long
import fetch_footage_long
import assemble_video_long
import upload_youtube_long

if __name__ == "__main__":
    print("=== LONG STEP 1: Script ===")
    generate_script_long.generate()
    print("=== LONG STEP 2: Voiceover ===")
    tts_gen_long.generate_all()
    print("=== LONG STEP 3: Footage ===")
    fetch_footage_long.fetch_all()
    print("=== LONG STEP 4: Assemble ===")
    assemble_video_long.assemble()
    print("=== LONG STEP 5: Upload ===")
    upload_youtube_long.upload()
    print("=== LONG DONE ===")
