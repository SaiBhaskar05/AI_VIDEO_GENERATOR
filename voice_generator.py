import edge_tts
import asyncio
import os


async def text_to_voice(text, cache_dir):

    os.makedirs(cache_dir, exist_ok=True)

    communicate = edge_tts.Communicate(
        text,
        "en-US-GuyNeural"          # male voice
    )

    await communicate.save(os.path.join(cache_dir, "voice.mp3"))


def generate_voice(script, cache_dir=".cache"):

    asyncio.run(text_to_voice(script, cache_dir))
