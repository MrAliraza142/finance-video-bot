"""
assemble_video_short.py
Builds final_video_short.mp4 (vertical 1080x1920) for YouTube Shorts.
Adds: crossfade transitions, Ken Burns zoom, outlined/glow-style captions,
a highlighted "Number of the Day" segment, and a branded intro title card.
"""

import json
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    TextClip,
    CompositeVideoClip,
    ColorClip,
    concatenate_videoclips,
)

W, H, CAPTION_H = 1080, 1920, 340
CROSSFADE = 0.3  # seconds of overlap between scenes

# MoneyPulse brand colors
NAVY = (13, 20, 40)
GOLD = (234, 179, 8)
GREEN = (16, 185, 129)


def apply_ken_burns(video, duration, zoom_amount=0.06):
    """Slow zoom-in over the clip's duration, output size stays fixed."""
    def resize_fn(t):
        return 1 + zoom_amount * (t / duration)
    zoomed = video.resize(resize_fn)
    return zoomed.crop(
        x_center=zoomed.w / 2, y_center=zoomed.h / 2, width=W, height=H
    )


def make_caption(text, is_number_of_day, fontsize):
    outline = TextClip(
        text, fontsize=fontsize, font="DejaVu-Sans-Bold",
        color="black", stroke_color="black", stroke_width=6,
        size=(W - 120, None), method="caption", align="center",
    )
    fill_color = GOLD if is_number_of_day else "white"
    fill = TextClip(
        text, fontsize=fontsize, font="DejaVu-Sans-Bold",
        color=fill_color, size=(W - 120, None), method="caption", align="center",
    )
    return CompositeVideoClip([outline, fill.set_position(("center", "center"))],
                               size=outline.size)


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
    video = apply_ken_burns(video, duration)
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
    # Small pop-in for the Number of the Day moment
    if is_number_of_day:
        caption = caption.resize(lambda t: 1 + 0.08 * max(0, 0.4 - t) if t < 0.4 else 1)

    scene_clip = CompositeVideoClip([video, bar, caption], size=(W, H))
    return scene_clip.crossfadein(CROSSFADE)


def make_intro_card(title):
    bg = ColorClip(size=(W, H), color=NAVY, duration=1.8)
    brand = TextClip(
        "MoneyPulse", fontsize=80, font="DejaVu-Sans-Bold", color=GREEN,
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
