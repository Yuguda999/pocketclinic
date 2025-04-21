from pydub import AudioSegment
from pydub.silence import split_on_silence
import tempfile

def preprocess_audio(audio_path: str) -> str:
    # Load the audio file
    audio = AudioSegment.from_file(audio_path)

    # Normalize volume
    normalized = audio.normalize()

    # Split on silence and keep only meaningful chunks
    chunks = split_on_silence(
        normalized,
        min_silence_len=500,     # ms
        silence_thresh=-40,      # dBFS
        keep_silence=250         # add back some silence buffer
    )

    # Recombine into a single clean audio segment
    if not chunks:
        return audio_path  # fallback if no chunk found

    cleaned_audio = AudioSegment.silent(duration=250)
    for chunk in chunks:
        cleaned_audio += chunk + AudioSegment.silent(duration=250)

    # Export to a temp WAV file for Whisper
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    cleaned_audio.export(tmp_file.name, format="wav")
    return tmp_file.name
