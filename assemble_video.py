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
    video = video.subclip(0,
