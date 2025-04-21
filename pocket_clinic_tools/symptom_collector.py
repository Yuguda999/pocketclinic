import os
import re
import tempfile
import base64
from crewai.tools import tool
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@tool("Collect Symptoms")
def collect_symptoms(audio_clip: bytes | None = None, text_message: str | None = None) -> dict:
    """
    Convert a short voice clip or SMS text into a structured symptom dict.
    Args:
        audio_clip: raw bytes of mp3/mp4/mpeg/m4a/wav/webm (≤25 MB)
        text_message: SMS text describing patient symptoms
    Returns:
        A dict with keys:
            fever (bool), cough (bool), difficulty_breathing (bool),
            diarrhea (bool), duration_days (int when present)
    """
    transcript = None

    if audio_clip:
        # Decode base64 if it's a string (coming from Crew)
        if isinstance(audio_clip, str):
            audio_clip = base64.b64decode(audio_clip)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_clip)
            tmp_path = tmp.name

        try:
            with open(tmp_path, "rb") as audio_file:
                resp = _client.audio.transcriptions.create(
                    model="gpt-4o-transcribe",  # ✅ This is the correct model
                    file=audio_file,
                    response_format="text"
                )
                transcript = resp
        finally:
            os.remove(tmp_path)  # ✅ Clean up temp file
    elif text_message:
        transcript = text_message
    else:
        return {"error": "Provide either 'audio_clip' or 'text_message'."}

    # DEBUG
    print(f"[DEBUG] Transcript: {transcript}")

    # 2) Regex extraction
    patterns = {
        "fever":                r"\bfever\b|\bhot\b|\btemperature\b",
        "cough":                r"\bcough\b|\bcoughing\b",
        "difficulty_breathing": r"difficulty breathing|shortness of breath",
        "diarrhea":             r"\bdiarrhea\b|\bloose stools\b",
        "duration_days":        r"(\d+)\s*(?:day|days)",
    }

    symptoms: dict[str, bool | int] = {}
    for key, pat in patterns.items():
        m = re.search(pat, transcript, re.IGNORECASE)
        if m:
            symptoms[key] = int(m.group(1)) if key == "duration_days" else True
        else:
            if key != "duration_days":
                symptoms[key] = False

    return symptoms
