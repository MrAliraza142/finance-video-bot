"""
assemble_video.py
Combines per-scene footage + audio + bold on-screen captions into one
final vertical (1080x1920) MP4 ready for YouTube Shorts / TikTok.
Uses MoviePy (built on free FFmpeg) - no paid tools involved.
"""

import json
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
    ColorClip,
)

W, H = 1080, 1920


def build_scene_clip(index, scene):
    audio = AudioFileClip(f"audio_scene_{index}.mp3")
    duration = audio.duration

    video = VideoFileClip(f"footage_scene_{index}.mp4")
    video = video.resize(height=H)
    if video.w < W:
        video = video.resize(width=W)
    video = video.crop(x_center=video.w / 2, y_center=video.h / 2, width=W, height=H)

    if video.duration < duration:
        loops = int(duration // video.duration) + 1
        video = concatenate_videoclips([video] * loops)
    video = video.subclip(0, duration).set_audio(audio)

    bar = ColorClip(size=(W, 340), color=(0, 0, 0)).set_opacity(0.55)
    bar = bar.set_position(("center", H - 380)).set_duration(duration)

    caption = TextClip(
        scene["on_screen_text"],
        fontsize=64,
        font="DejaVu-Sans-Bold",
        color="white",
        size=(W - 120, None),
        method="caption",
        align="center",
    )
    caption = caption.set_position(("center", H - 340)).set_duration(duration)

    return CompositeVideoClip([video, bar, caption], size=(W, H))


def assemble():
    with open("today_script.json") as f:
        data = json.load(f)

    clips = [build_scene_clip(i, scene) for i, scene in enumerate(data["scenes"])]
    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(
        "final_video.mp4",
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=4,
    )
    print("final_video.mp4 created")


if __name__ == "__main__":
    assemble()
