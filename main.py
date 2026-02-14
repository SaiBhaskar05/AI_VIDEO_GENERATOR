from script_generator import generate_script
from voice_generator import generate_voice
from visuals import download_visual
from video_merge import merge_video


def run_pipeline(topic, on_status=None):
    """Run the full pipeline. Optionally call on_status(step, detail) for UI."""

    def _status(step, detail=""):
        if on_status:
            on_status(step, detail)
        print(f"[{step}] {detail}")

    _status("script", "Generating script...")
    script = generate_script(topic)
    _status("script_done", script)

    _status("voice", "Generating voice...")
    generate_voice(script)
    _status("voice_done", "voice.mp3 ready")

    _status("visuals", "Downloading images & clips...")
    media = download_visual(topic)
    _status("visuals_done", str(media))

    _status("merge", "Merging final video...")
    merge_video()
    _status("merge_done", "final_video.mp4 ready")

    return "final_video.mp4"


if __name__ == "__main__":

    topic = input("Enter video topic: ")
    run_pipeline(topic)
