from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import textwrap
import os
import requests
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")


def fetch_thumbnail_image(topic, output_dir="cache"):
    """Fetch a high-quality cinematic image from Pexels specifically for the thumbnail."""
    os.makedirs(output_dir, exist_ok=True)
    headers = {"Authorization": PEXELS_API_KEY}

    # Try multiple search queries — from specific to broad
    queries = [
        f"{topic} cinematic background",
        f"{topic} wallpaper",
        topic,
    ]

    for query in queries:
        try:
            url = (
                f"https://api.pexels.com/v1/search"
                f"?query={query}&per_page=1&orientation=landscape&size=large"
            )
            r = requests.get(url, headers=headers, timeout=10)
            photos = r.json().get("photos", [])
            if photos:
                link = photos[0]["src"]["original"]
                data = requests.get(link, timeout=15).content
                path = os.path.join(output_dir, "thumbnail_bg.jpg")
                with open(path, "wb") as f:
                    f.write(data)
                print(f"Thumbnail background fetched for query: '{query}'")
                return path
        except Exception as e:
            print(f"Thumbnail image fetch failed for '{query}': {e}")
            continue

    print("No thumbnail background found from Pexels, using gradient fallback.")
    return None


def generate_thumbnail(topic, output_dir="cache", bg_image_path=None):
    """Generate a YouTube-style thumbnail with topic text and optional background image."""
    width, height = 1280, 720

    # Use Pexels image as background, or fallback to gradient
    if bg_image_path and os.path.exists(bg_image_path):
        img = Image.open(bg_image_path).resize((width, height))
        # Keep image clearly visible — only slight darken, no blur
        img = ImageEnhance.Brightness(img).enhance(0.7)
        img = ImageEnhance.Contrast(img).enhance(1.2)
    else:
        img = Image.new("RGB", (width, height), color=(15, 15, 35))
        draw = ImageDraw.Draw(img)
        for y in range(height):
            r = int(15 + (y / height) * 40)
            g = int(15 + (y / height) * 20)
            b = int(35 + (y / height) * 60)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Light overlay only at bottom half for text readability (gradient effect)
    img = img.convert("RGBA")
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    for y in range(height // 3, height):
        alpha = int(180 * ((y - height // 3) / (height - height // 3)))
        overlay_draw.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    # Load fonts
    try:
        font_large = ImageFont.truetype("arial.ttf", 60)
        font_small = ImageFont.truetype("arial.ttf", 28)
    except OSError:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Place topic text in bottom third so the image stays visible
    wrapped = textwrap.wrap(topic.upper(), width=28)
    line_height = 72
    total_text_height = len(wrapped) * line_height
    y_offset = height - total_text_height - 80  # 80px from bottom

    for line in wrapped:
        bbox = draw.textbbox((0, 0), line, font=font_large)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        # Thick shadow for readability
        for dx, dy in [(-2,-2),(2,-2),(-2,2),(2,2),(0,-3),(0,3),(-3,0),(3,0)]:
            draw.text((x + dx, y_offset + dy), line, fill=(0, 0, 0), font=font_large)
        # Main text — bright yellow for pop
        draw.text((x, y_offset), line, fill=(255, 255, 50), font=font_large)
        y_offset += line_height

    # Save
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "thumbnail.png")
    img = img.convert("RGB")
    img.save(path)
    print(f"Thumbnail saved to {path}")
    return path
