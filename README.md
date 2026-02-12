# 🎥 AI Video Generator

An AI-powered video generation pipeline built with **Streamlit**. Enter a topic and the app automatically writes a script, generates a voiceover, downloads relevant visuals, and merges everything into a final video — all in one click.

## Features

- **AI Script Writing** — Generates a 1-minute spoken script using Google Gemini
- **Text-to-Speech** — Converts the script to a natural male voiceover using Edge TTS
- **Auto Visuals** — Downloads royalty-free video clips and images from Pexels
- **Video Merging** — Interleaves clips and images, syncs with audio, and exports the final video
- **Multi-User Support** — Each session gets an isolated cache directory, so multiple users can generate videos simultaneously without conflicts
- **Auto Cleanup** — Stale session caches are automatically deleted after 30 minutes

## ⚠️ Note on Visuals

This app uses the **Pexels API** to fetch royalty-free images and video clips. Since Pexels is a community-driven stock media platform, **it may not have relevant or accurate visuals for every topic**. For niche, highly specific, or trending topics, the downloaded images and clips might not closely match the subject. The generated video will still be produced, but the visuals may be generic or loosely related.

## Tech Stack

| Component | Technology |
|---|---|
| UI | Streamlit |
| Script Generation | Google Gemini (gemini-2.5-flash) |
| Voice Generation | Edge TTS |
| Visuals | Pexels API (royalty-free) |
| Video Processing | MoviePy + FFmpeg |

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/ai-video-generator.git
cd ai-video-generator
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg

FFmpeg is required by MoviePy for video processing.

- **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
- **macOS:** `brew install ffmpeg`
- **Linux:** `sudo apt install ffmpeg`

### 4. Set up environment variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
PEXELS_API_KEY=your_pexels_api_key_here
```

Get your API keys from:
- **Gemini:** [Google AI Studio](https://aistudio.google.com/apikey)
- **Pexels:** [Pexels API](https://www.pexels.com/api/)

### 5. Run the app

```bash
streamlit run app.py
```

## Project Structure

```
├── app.py                 # Streamlit UI and pipeline orchestration
├── script_generator.py    # AI script generation using Gemini
├── voice_generator.py     # Text-to-speech using Edge TTS
├── visuals.py             # Image and video download from Pexels
├── video_merge.py         # Video merging and encoding with MoviePy
├── requirements.txt       # Python dependencies
├── .env                   # API keys (not committed)
└── .gitignore             # Git ignore rules
```

## Deployment (Streamlit Cloud)

1. Push the repo to GitHub (make sure `.env` is in `.gitignore`)
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo
3. Set `app.py` as the main file
4. Add a `packages.txt` with `ffmpeg` for the system dependency
5. Add your API keys in **Settings → Secrets**:
   ```toml
   GEMINI_API_KEY = "your_key"
   PEXELS_API_KEY = "your_key"
   ```

