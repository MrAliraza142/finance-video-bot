"""
assemble_video.py
Builds TWO final videos:
  - final_video_short.mp4  (vertical 1080x1920, for YouTube Shorts)
  - final_video_long.mp4   (landscape 1920x1080, for a regular video)
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


def build_scene_clip(audio_path, video_path, caption_text, W, H, caption_h):
    audio = AudioFileClip(audio_path)
    duration = audio.duration

    video = VideoFileClip(video_path)
    video = video.resize(height=H)
    if video.w < W:
        video = video.resize(width=W)
    video = video.crop(x_center=video.w / 2, y_center=video.h / 2, width=W, height=H)

    if video.duration < duration:
        loops = int(duration // video.duration) + 1
        video = concatenate_videoclips([video] * loops)
    video = video.subclip(0, duration)
    video = video.set_audio(audio)

    bar = ColorClip(size=(W, caption_h), color=(0, 0, 0))
    bar = bar.set_opacity(0.55)
    bar = bar.set_position(("center", H - caption_h - 40))
    bar = bar.set_duration(duration)

    caption = TextClip(
        caption_text,
        fontsize=int(W * 0.05),
        font="DejaVu-Sans-Bold",
        color="white",
        size=(W - 120, None),
        method="caption",
        align="center",
    )
    caption = caption.set_position(("center", H - caption_h))
    caption = caption.set_duration(duration)

    return CompositeVideoClip([video, bar, caption], size=(W, H))


def build_video(scenes, prefix, W, H, caption_h, out_path):
    clips = []
    for i, scene in enumerate(scenes):
        audio_file = "audio_" + prefix + "_" + str(i) + ".mp3"
        video_file = "footage_" + prefix + "_" + str(i) + ".mp4"
        clip = build_scene_clip(
            audio_file,
            video_file,
            scene["on_screen_text"],
            W, H, caption_h,
        )
        clips.append(clip)
    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(out_path, fps=30, codec="libx264", audio_codec="aac", threads=4)


def assemble():
    with open("today_script.json") as f:
        data = json.load(f)

    print("Building SHORT video...")
    build_video(data["short"]["scenes"], "short", 1080, 1920, 340, "final_video_short.mp4")

    print("Building LONG video...")
    build_video(data["long"]["scenes"], "long", 1920, 1080, 220, "final_video_long.mp4")

    print("Both videos created.")


if __name__ == "__main__":
    assemble()
