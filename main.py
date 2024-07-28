import requests
import os
import random
from datetime import date
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import (
    ImageClip,
    TextClip,
    CompositeVideoClip,
    AudioFileClip,
    ColorClip,
)

FONT_LOC = "assets/MonoLisa-Regular.ttf"


def get_random_fact():
    response = requests.get("https://uselessfacts.jsph.pl/random.json?language=en")
    fact_text = response.json()["text"]

    with open("facts.txt", "a") as file:
        file.write(f"{date.today()} {fact_text}\n")

    return fact_text


def create_fact_image(fact, width=1080, height=1920):
    img = Image.new("RGB", (width, height), color="black")
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_LOC, 60)

    # Define padding
    padding_x = 100  # Horizontal padding

    # Wrap text
    lines = []
    words = fact.split()
    current_line = words[0]
    max_width = width - (2 * padding_x)  # Account for left and right padding

    for word in words[1:]:
        line_width, _ = d.textbbox((0, 0), current_line + " " + word, font=font)[2:4]
        if line_width <= max_width:
            current_line += " " + word
        else:
            lines.append(current_line)
            current_line = word

    lines.append(current_line)

    # Calculate total text height
    total_text_height = (
        sum(d.textbbox((0, 0), line, font=font)[3] for line in lines)
        + (len(lines) - 1) * 20
    )

    # Draw text
    y_text = (height - total_text_height) // 2  # Center text vertically
    for line in lines:
        line_width, line_height = d.textbbox((0, 0), line, font=font)[2:4]
        x_text = (width - line_width) // 2  # Center each line horizontally
        d.text((x_text, y_text), line, font=font, fill="white")
        y_text += line_height + 20

    return np.array(img)


# def create_fact_video(fact):
#     width, height = 1080, 1920
#     duration = 10

#     # Create background
#     bg = ColorClip((width, height), color=(0, 0, 0), duration=duration)

#     # Create fact image
#     img = create_fact_image(fact, width, height)
#     img_clip = ImageClip(img).set_duration(duration)

#     # Create title
#     title_clip = TextClip(
#         "Daily Fact",
#         fontsize=70,
#         color="white",
#         font="assets/MonoLisa-Regular.ttf",
#         size=(width, 100),
#     )
#     title_clip = title_clip.set_position(("center", 100)).set_duration(duration)

#     # Add fade effects
#     img_clip = img_clip.crossfadein(1).fadeout(1)
#     title_clip = title_clip.crossfadein(1).fadeout(1)

#     # Compose video
#     video = CompositeVideoClip([bg, img_clip, title_clip])

#     # Add background music (ensure you have rights to use the audio)
#     try:
#         audio = (
#             AudioFileClip("background_music.mp3").subclip(0, duration).audio_fadeout(1)
#         )
#         video = video.set_audio(audio)
#     except Exception as e:
#         print(f"Error adding background music: {e}")
#         print("Creating video without audio.")

#     # Write video file
#     video.write_videofile("daily_fact.mp4", fps=24)


def generate_unique_filename(base_path, initial_number=1):
    """
    Generates a unique file name by appending a number if needed.

    Args:
        base_path: The base path with file name and extension.
        initial_number: The starting number for appending.

    Returns:
        A unique file path with an incremented number.
    """
    directory, filename = os.path.split(base_path)
    name, ext = os.path.splitext(filename)

    new_path = base_path
    num = initial_number

    while os.path.exists(new_path):
        new_path = os.path.join(directory, f"{name}_{num}{ext}")
        num += 1

    return new_path


def create_fact_video(
    fact,
    audio_files_dir,
    output_file,
    width=1080,
    height=1920,
    duration=10,
    fps=60,
):
    """
    Creates a video with a given fact, optional background music, and customizable parameters.

    Args:
        fact: The fact to display.
        audio_files_dir: Directory containing audio files (optional).
        output_file: Output video file path (default: "daily_fact.mp4").
        width: Video width (default: 1080).
        height: Video height (default: 1920).
        duration: Video duration (default: 10).
        fps: Frames per second (default: 60).
    """

    # Create background
    bg = ColorClip((width, height), color=(0, 0, 0), duration=duration)

    # Create fact image
    img = create_fact_image(fact, width, height)
    img_clip = ImageClip(img).set_duration(duration)

    # Create title
    title_clip = TextClip(
        "Random Fact",
        fontsize=70,
        color="white",
        font=FONT_LOC,
        size=(width, 100),
    )
    title_clip = title_clip.set_position(("center", 100)).set_duration(duration)

    # Add fade effects
    img_clip = img_clip.crossfadein(1).fadeout(1)
    title_clip = title_clip.crossfadein(1).fadeout(1)

    # Compose video
    video = CompositeVideoClip([bg, img_clip, title_clip])

    # Add background music
    if audio_files_dir:
        # audio_files = [
        #     f for f in os.listdir(audio_files_dir) if f.endswith((".mp3", ".wav"))
        # ]
        # audio_file = random.choice(audio_files)
        # audio_path = os.path.join(audio_files_dir, audio_file)
        # audio = AudioFileClip(audio_path).subclip(0, duration).audio_fadeout(1)
        # video = video.set_audio(audio)

        audio_files = [
            f for f in os.listdir(audio_files_dir) if f.endswith((".mp3", ".wav"))
        ]
        audio_file = random.choice(audio_files)
        audio_path = os.path.join(audio_files_dir, audio_file)

        # Load the audio file
        audio_clip = AudioFileClip(audio_path)
        audio_length = audio_clip.duration

        # Calculate the start time
        if audio_length > duration:
            start_time = random.uniform(0, audio_length - duration)
        else:
            start_time = 0

        # Create a subclip with the desired duration
        audio_subclip = audio_clip.subclip(
            start_time, start_time + duration
        ).audio_fadeout(1)
        video = video.set_audio(audio_subclip)

    file_name = generate_unique_filename(output_file)

    # Write video file
    video.write_videofile(file_name, fps=fps)


if __name__ == "__main__":
    fact = get_random_fact()
    create_fact_video(
        fact=fact,
        output_file=f"videos/{date.today()}_daily_fact.mp4",
        audio_files_dir="music",
    )
