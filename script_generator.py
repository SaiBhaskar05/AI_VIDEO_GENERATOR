from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure API key
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_script(topic, cache_dir=".cache"):

    os.makedirs(cache_dir, exist_ok=True)

    prompt = f"""
You are a friendly male speaker talking directly to the viewer.
Write a 1-minute spoken script about: {topic}.
The script MUST be between 150 and 160 words so it lasts exactly 1 minute
when read at a natural pace.

Rules:
- Output ONLY the words the speaker will say out loud.
- Do NOT include any headings, titles, section labels, timestamps,
  stage directions, music cues, or formatting of any kind.
- Do NOT use markdown, bullet points, numbered lists, or asterisks.
- Write in a natural, conversational, first-person tone as if a real
  person is talking to a friend.
- Start speaking immediately — no intro like "Welcome to..." unless
  it feels natural.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    script = clean_script(response.text)

    with open(os.path.join(cache_dir, "script.txt"), "w", encoding="utf-8") as f:
        f.write(script)

    return script


def clean_script(text: str) -> str:
    """Remove any leftover headings, markdown, or metadata lines
    so only pure spoken content remains."""
    import re
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        stripped = line.strip()
        # Skip markdown headings
        if stripped.startswith("#"):
            continue
        # Skip lines that look like stage directions [MUSIC], (pause), etc.
        if re.match(r'^[\[\(].*[\]\)]$', stripped):
            continue
        # Remove bold/italic markers
        stripped = re.sub(r'[\*_]{1,3}', '', stripped)
        if stripped:
            cleaned.append(stripped)
    return "\n".join(cleaned)
