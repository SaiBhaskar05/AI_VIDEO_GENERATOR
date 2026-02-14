import math
import glob
import os
import shutil
from moviepy import (
    VideoFileClip, AudioFileClip, ImageClip,
    concatenate_videoclips, vfx
)

TARGET_W, TARGET_H = 1280, 720
IMAGE_DURATION = 4  # seconds each image is shown


def _resize_clip(clip):
    """Resize any clip to exactly TARGET_W x TARGET_H."""
    return clip.resized((TARGET_W, TARGET_H))


def merge_video(cache_dir=".cache"):

    print("Merging video and audio...")

    # --- Collect video clips from cache ---
    vid_paths = sorted(glob.glob(os.path.join(cache_dir, "visual_v*.mp4")))
    vid_clips = [_resize_clip(VideoFileClip(p)) for p in vid_paths]

    # --- Collect image clips from cache ---
    img_paths = sorted(glob.glob(os.path.join(cache_dir, "visual_i*.jpg")))
    img_clips = []
    for p in img_paths:
        img = (ImageClip(p)
               .with_duration(IMAGE_DURATION)
               .resized((TARGET_W, TARGET_H))
               .with_effects([vfx.CrossFadeIn(0.5)]))
        img_clips.append(img)

    # Interleave: video, image, video, image, ...
    all_clips = []
    vi, ii = 0, 0
    while vi < len(vid_clips) or ii < len(img_clips):
        if vi < len(vid_clips):
            all_clips.append(vid_clips[vi])
            vi += 1
        if ii < len(img_clips):
            all_clips.append(img_clips[ii])
            ii += 1

    if not all_clips:
        raise RuntimeError("No visual clips or images found in cache.")

    audio = AudioFileClip(os.path.join(cache_dir, "voice.mp3"))
    audio_duration = audio.duration
    print(f"Audio duration: {audio_duration:.1f}s")

    # Concatenate all
    combined = concatenate_videoclips(all_clips, method="compose")
    print(f"Combined visuals duration: {combined.duration:.1f}s")

    # Loop if still too short
    if combined.duration < audio_duration:
        loops = math.ceil(audio_duration / combined.duration)
        combined = concatenate_videoclips([combined] * loops, method="compose")
        print(f"Looped visuals {loops}x")

    # Trim to audio length
    combined = combined.subclipped(0, audio_duration)

    # Attach audio
    final_video = combined.with_audio(audio)

    # Export into cache first
    cache_output = os.path.join(cache_dir, "final_video.mp4")
    final_video.write_videofile(
        cache_output,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        threads=4,
        fps=24
    )

    # Close all clips so files are released
    for c in vid_clips:
        c.close()
    for c in img_clips:
        c.close()
    audio.close()
    combined.close()
    final_video.close()

    # Move final video out of cache to project root
    shutil.move(cache_output, "final_video.mp4")
    print("Moved final_video.mp4 to project root")

    # Delete the session cache folder
    shutil.rmtree(cache_dir, ignore_errors=True)
    print("🧹 Cache cleaned up")

    print("✅ Final video generated!")
