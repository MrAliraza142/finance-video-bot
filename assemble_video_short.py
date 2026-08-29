"""
assemble_video_short.py
Builds final_video_short.mp4 (vertical 1080x1920) for YouTube Shorts.
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

W, H, CAPTION_H = 1080, 1920, 340


def build_scene_clip(i, scene):
    audio = AudioFileClip(f"audio_short_{i}.mp3")
    duration = audio.duration

    video = VideoFileClip(f"footage_short_{i}.mp4")
    video = video.resize(height=H)
    if video.w < W:
        video = video.resize(width=W)
    video = video.crop(x_center=video.w / 2, y_center=video.h / 2, width=W, height=H)

    if video.duration < duration:
        loops = int(duration // video.duration) + 1
        video = concatenate_videoclips([video] * loops)
    video = video.subclip(0, duration)
    video = video.set_audio(audio)

    bar = ColorClip(size=(W, CAPTION_H), color=(0, 0, 0))
    bar = bar.set_opacity(0.55)
    bar = bar.set_position(("center", H - CAPTION_H - 40))
    bar = bar.set_duration(duration)

    caption = TextClip(
        scene["on_screen_text"],
        fontsize=64,
        font="DejaVu-Sans-Bold",
        color="white",
        size=(W - 120, None),
        method="caption",
        align="center",
    )
    caption = caption.set_position(("center", H - CAPTION_H))
    caption = caption.set_duration(duration)

    return CompositeVideoClip([video, bar, caption], size=(W, H))


def assemble():
    with open("today_script_short.json") as f:
        data = json.load(f)
    clips = [build_scene_clip(i, s) for i, s in enumerate(data["scenes"])]
    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile("final_video_short.mp4", fps=30, codec="libx264", audio_codec="aac", threads=4)
    print("final_video_short.mp4 created")


if __name__ == "__main__":
    assemble()
