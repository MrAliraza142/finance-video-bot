"""
assemble_video_short.py
Builds final_video_short.mp4 (vertical 1080x1920) for YouTube Shorts.
Professional edition: crossfade transitions, per-scene static zoom variation
(cheap - applied once, not animated per-frame), outlined captions, a
highlighted "Number of the Day" segment, and a branded intro title card.
"""

import json
import random
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    TextClip,
    CompositeVideoClip,
    ColorClip,
    concatenate_videoclips,
)

W, H, CAPTION_H = 1080, 1920, 340
CROSSFADE = 0.3

NAVY = (13, 20, 40)
GOLD = (234, 179, 8)
GOLD_HEX = "#EAB308"
GREEN_HEX = "#10B981"


def make_caption(text, is_number_of_day, fontsize):
    fill_color = GOLD_HEX if is_number_of_day else "white"
    return TextClip(
        text, fontsize=fontsize, font="DejaVu-Sans-Bold",
        color=fill_color, stroke_color="black", stroke_width=3,
        size=(W - 120, None), method="caption", align="center",
    )


def build_scene_clip(i, scene):
    audio = AudioFileClip(f"audio_short_{i}.mp3")
    duration = audio.duration

    video = VideoFileClip(f"footage_short_{i}.mp4")
    video = video.resize(height=H)
    if video.w < W:
        video = video.resize(width=W)

    zoom_factor = 1.0 + (0.10 if i % 2 == 0 else 0.16)
    video = video.resize(zoom_factor)
    video = video.crop(x_center=video.w / 2, y_center=video.h / 2, width=W, height=H)

    if video.duration < duration:
        loops = int(duration // video.duration) + 1
        video = concatenate_videoclips([video] * loops)
    video = video.subclip(0, duration)
    video = video.set_audio(audio)

    on_screen_text = scene["on_screen_text"]
    is_number_of_day = on_screen_text.upper().startswith("NUMBER OF THE DAY")

    bar_color = GOLD if is_number_of_day else NAVY
    bar = ColorClip(size=(W, CAPTION_H), color=bar_color)
    bar = bar.set_opacity(0.65 if is_number_of_day else 0.55)
    bar = bar.set_position(("center", H - CAPTION_H - 40))
    bar = bar.set_duration(duration)

    caption = make_caption(on_screen_text, is_number_of_day, fontsize=68 if is_number_of_day else 64)
    caption = caption.set_position(("center", H - CAPTION_H))
    caption = caption.set_duration(duration)

    scene_clip = CompositeVideoClip([video, bar, caption], size=(W, H))
    return scene_clip.crossfadein(CROSSFADE)


def make_intro_card(title):
    bg = ColorClip(size=(W, H), color=NAVY, duration=1.8)
    brand = TextClip(
        "MoneyPulse", fontsize=80, font="DejaVu-Sans-Bold", color=GREEN_HEX,
    ).set_position(("center", H / 2 - 160)).set_duration(1.8)
    headline = TextClip(
        title, fontsize=46, font="DejaVu-Sans-Bold", color="white",
        size=(W - 160, None), method="caption", align="center",
    ).set_position(("center", H / 2 - 30)).set_duration(1.8)
    card = CompositeVideoClip([bg, brand, headline], size=(W, H))
    return card.fadein(0.3).fadeout(0.3)


def assemble():
    with open("today_script_short.json") as f:
        data = json.load(f)

    scene_clips = [build_scene_clip(i, s) for i, s in enumerate(data["scenes"])]
    intro = make_intro_card(data.get("title", "MoneyPulse"))

    all_clips = [intro] + scene_clips
    final = concatenate_videoclips(all_clips, method="compose", padding=-CROSSFADE)
    final.write_videofile("final_video_short.mp4", fps=30, codec="libx264", audio_codec="aac", threads=4)
    print("final_video_short.mp4 created")


if __name__ == "__main__":
    assemble()
