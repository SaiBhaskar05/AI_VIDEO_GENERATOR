import streamlit as st
import glob
import os
import shutil
import uuid
import time
from script_generator import generate_script
from voice_generator import generate_voice
from visuals import download_visual
from video_merge import merge_video
from thumbnail_generator import generate_thumbnail, fetch_thumbnail_image

SESSION_TIMEOUT = 30 * 60  # 30 minutes


def cleanup_stale_sessions():
    """Remove session cache folders older than SESSION_TIMEOUT seconds."""
    cache_root = ".cache"
    if not os.path.exists(cache_root):
        return
    now = time.time()
    for folder in os.listdir(cache_root):
        folder_path = os.path.join(cache_root, folder)
        if os.path.isdir(folder_path):
            age = now - os.path.getmtime(folder_path)
            if age > SESSION_TIMEOUT:
                shutil.rmtree(folder_path, ignore_errors=True)


# Clean up abandoned session caches on every app load
cleanup_stale_sessions()

# Per-session cache directory so multiple users don't collide
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

CACHE_DIR = os.path.join(".cache", st.session_state.session_id)

st.set_page_config(page_title="AI Video Generator", layout="wide")

st.title("🎥 AI Video Generation Pipeline")
st.markdown("Enter a topic and watch each step happen in real time.")

topic = st.text_input("Enter Video Topic", placeholder="e.g. Morning Routine Tips")

if st.button("🚀 Generate Video", type="primary", use_container_width=True):

    if not topic:
        st.warning("Please enter a topic.")
        st.stop()

    # Clean any leftover cache from a previous run
    if os.path.exists(CACHE_DIR):
        shutil.rmtree(CACHE_DIR, ignore_errors=True)

    progress = st.progress(0, text="Starting pipeline...")

    # ── Step 1: Script ──────────────────────────────────────────────
    with st.status("📝 Generating script...", expanded=True) as status:
        st.write("Asking AI to write a 1-minute spoken script...")
        script = generate_script(topic, CACHE_DIR)
        word_count = len(script.split())
        st.text_area("Generated Script", script, height=180, disabled=True)
        st.caption(f"{word_count} words ≈ {word_count / 150:.1f} min at natural pace")
        status.update(label="✅ Script ready (cached)", state="complete")
    progress.progress(25, text="Script generated")

    # ── Step 2: Voice ───────────────────────────────────────────────
    with st.status("🎙️ Generating male voice...", expanded=True) as status:
        st.write("Converting script to speech (cached in .cache/)...")
        generate_voice(script, CACHE_DIR)
        voice_path = os.path.join(CACHE_DIR, "voice.mp3")
        st.audio(voice_path)
        status.update(label="✅ Voice ready (cached)", state="complete")
    progress.progress(50, text="Voice generated")

    # ── Step 3: Visuals ─────────────────────────────────────────────
    with st.status("🖼️ Downloading images & clips to cache...", expanded=True) as status:
        st.write("Fetching relevant visuals from Pexels into .cache/ ...")
        media = download_visual(topic, CACHE_DIR)

        # Show cached images
        images = sorted(glob.glob(os.path.join(CACHE_DIR, "visual_i*.jpg")))
        if images:
            st.write(f"**{len(images)} images downloaded (cached):**")
            cols = st.columns(min(len(images), 5))
            for idx, img_path in enumerate(images):
                with cols[idx % len(cols)]:
                    st.image(img_path, use_container_width=True,
                             caption=os.path.basename(img_path))

        # Show cached video clips
        clips = sorted(glob.glob(os.path.join(CACHE_DIR, "visual_v*.mp4")))
        if clips:
            st.write(f"**{len(clips)} video clips downloaded (cached):**")
            clip_cols = st.columns(min(len(clips), 3))
            for idx, clip_path in enumerate(clips):
                with clip_cols[idx % len(clip_cols)]:
                    st.video(clip_path)
                    st.caption(os.path.basename(clip_path))

        status.update(label=f"✅ {len(images)} images + {len(clips)} clips cached",
                      state="complete")
    progress.progress(75, text="Visuals downloaded")

    # ── Step 4: Merge ───────────────────────────────────────────────
    with st.status("🎬 Merging final video...", expanded=True) as status:
        st.write("Resizing → interleaving → encoding → cleaning cache...")
        merge_video(CACHE_DIR)  # this also cleans up cache after moving final_video.mp4 out
        status.update(label="✅ Video merged & cache cleaned", state="complete")
    progress.progress(100, text="Done!")

    # ── Step 5: Thumbnail ────────────────────────────────────────────
    with st.status("🖼️ Generating thumbnail...", expanded=True) as status:
        st.write("Fetching a cinematic background image for thumbnail...")
        bg_image = fetch_thumbnail_image(topic, output_dir=CACHE_DIR)
        st.write("Creating YouTube-style thumbnail...")
        thumbnail_path = generate_thumbnail(topic, output_dir=CACHE_DIR, bg_image_path=bg_image)
        status.update(label="✅ Thumbnail ready", state="complete")

    # ── Final Output ────────────────────────────────────────────────
    st.balloons()
    st.success("✅ Video Generated Successfully!")

    st.divider()
    st.subheader("🎬 Your Generated Content")

    # Video and Thumbnail side by side
    col_video, col_thumb = st.columns([3, 2], gap="large")
    with col_video:
        st.markdown("**📹 Final Video**")
        st.video("final_video.mp4")
        with open("final_video.mp4", "rb") as f:
            st.download_button(
                label="⬇️ Download Video",
                data=f,
                file_name=f"{topic.replace(' ', '_')}_video.mp4",
                mime="video/mp4",
                use_container_width=True
            )
    with col_thumb:
        st.markdown("**🖼️ Thumbnail**")
        st.image(thumbnail_path, use_container_width=True)
        if os.path.exists(thumbnail_path):
            with open(thumbnail_path, "rb") as f:
                st.download_button(
                    label="📥 Download Thumbnail",
                    data=f,
                    file_name=f"{topic.replace(' ', '_')}_thumbnail.png",
                    mime="image/png",
                    use_container_width=True
                )

    st.divider()
    st.info("🧹 Session cache has been deleted. Only final_video.mp4 remains.")
