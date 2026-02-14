import requests
import os
import glob
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

TARGET_W, TARGET_H = 1280, 720


def download_visual(topic, cache_dir=".cache"):
    """Download topic-relevant video clips AND images into cache."""

    os.makedirs(cache_dir, exist_ok=True)

    # Clean up old cached visuals
    for old in glob.glob(os.path.join(cache_dir, "visual_*.*")):
        os.remove(old)

    headers = {"Authorization": PEXELS_API_KEY}
    saved_videos = []
    saved_images = []

    # --- Download video clips (3) ---
    vid_url = (
        f"https://api.pexels.com/videos/search"
        f"?query={topic}&per_page=3&orientation=landscape"
    )
    r = requests.get(vid_url, headers=headers)
    videos = r.json().get("videos", [])

    for i, video in enumerate(videos):
        files = video.get("video_files", [])
        best = min(files, key=lambda f: abs((f.get("height") or 9999) - TARGET_H))
        link = best["link"]
        print(f"Downloading clip {i+1}/{len(videos)}: {best.get('width')}x{best.get('height')}")
        data = requests.get(link).content
        path = os.path.join(cache_dir, f"visual_v{i}.mp4")
        with open(path, "wb") as f:
            f.write(data)
        saved_videos.append(path)

    # --- Download images (5) ---
    img_url = (
        f"https://api.pexels.com/v1/search"
        f"?query={topic}&per_page=5&orientation=landscape"
    )
    r = requests.get(img_url, headers=headers)
    photos = r.json().get("photos", [])

    for i, photo in enumerate(photos):
        link = photo["src"]["large2x"]
        print(f"Downloading image {i+1}/{len(photos)}")
        data = requests.get(link).content
        path = os.path.join(cache_dir, f"visual_i{i}.jpg")
        with open(path, "wb") as f:
            f.write(data)
        saved_images.append(path)

    print(f"Downloaded {len(saved_videos)} clips + {len(saved_images)} images for '{topic}'")
    return {"videos": saved_videos, "images": saved_images}
