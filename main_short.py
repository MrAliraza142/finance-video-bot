"""
main_short.py
Runs the full SHORT pipeline: auth check -> script -> voice -> footage ->
assemble -> upload.
The auth check runs FIRST so an expired/revoked YouTube token fails in
seconds, instead of after several minutes of video processing.
"""

import upload_youtube_short
import generate_script_short
import tts_gen_short
import fetch_footage_short
import assemble_video_short

if __name__ == "__main__":
    print("=== SHORT STEP 0: Verify YouTube auth ===")
    upload_youtube_short.get_service()  # fails fast with clear message if token is bad

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
