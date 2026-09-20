"""
assemble_video_long.py
Builds final_video_long.mp4 (landscape 1920x1080) for a regular video.
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

W, H, CAPTION_H = 1920, 1080, 220
CROSSFADE = 0.35  # seconds of overlap between scenes

# MoneyPulse brand colors
# RGB tuples are for ColorClip (solid background bars).
# Hex strings are for TextClip (text color must be a name or hex string).
NAVY = (13, 20, 40)
GOLD = (234, 179, 8)

GOLD_HEX = "#EAB308"
GREEN_HEX = "#10B981"


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
        size=(W - 200, None), method="caption", align="center",
    )
    fill_color = GOLD_HEX if is_number_of_day else "white"
    fill = TextClip(
        text, fontsize=fontsize, font="DejaVu-Sans-Bold",
        color=fill_color, size=(W - 200, None), method="caption", align="center",
    )
    return CompositeVideoClip([outline, fill.set_position(("center", "center"))],
                               size=outline.size)


def build_scene_clip(i, scene):
    audio = AudioFileClip(f"audio_long_{i}.mp3")
    duration = audio.duration

    video = VideoFileClip(f"footage_long_{i}.mp4")
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
    bar = bar.set_position(("center", H - CAPTION_H - 30))
    bar = bar.set_duration(duration)

    caption = make_caption(on_screen_text, is_number_of_day, fontsize=52 if is_number_of_day else 48)
    caption = caption.set_position(("center", H - CAPTION_H))
    caption = caption.set_duration(duration)
    # Small pop-in for the Number of the Day moment
    if is_number_of_day:
        caption = caption.resize(lambda t: 1 + 0.08 * max(0, 0.4 - t) if t < 0.4 else 1)

    scene_clip = CompositeVideoClip([video, bar, caption], size=(W, H))
    return scene_clip.crossfadein(CROSSFADE)


def make_intro_card(title):
    bg = ColorClip(size=(W, H), color=NAVY, duration=2.5)
    brand = TextClip(
        "MoneyPulse", fontsize=90, font="DejaVu-Sans-Bold", color=GREEN_HEX,
    ).set_position(("center", H / 2 - 140)).set_duration(2.5)
    headline = TextClip(
        title, fontsize=54, font="DejaVu-Sans-Bold", color="white",
        size=(W - 300, None), method="caption", align="center",
    ).set_position(("center", H / 2 - 20)).set_duration(2.5)
    card = CompositeVideoClip([bg, brand, headline], size=(W, H))
    return card.fadein(0.4).fadeout(0.4)


def assemble():
    with open("today_script_long.json") as f:
        data = json.load(f)

    scene_clips = [build_scene_clip(i, s) for i, s in enumerate(data["scenes"])]
    intro = make_intro_card(data.get("title", "MoneyPulse"))

    all_clips = [intro] + scene_clips
    final = concatenate_videoclips(all_clips, method="compose", padding=-CROSSFADE)
    final.write_videofile("final_video_long.mp4", fps=30, codec="libx264", audio_codec="aac", threads=4)
    print("final_video_long.mp4 created")


if __name__ == "__main__":
    assemble()
