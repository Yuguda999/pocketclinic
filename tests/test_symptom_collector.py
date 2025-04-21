import os
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pocket_clinic_tools.symptom_collector import collect_symptoms


def main():
    # Instantiate the tool

    # ─── Text‑message tests ───────────────────────────────────────────────────────
    print("=== Text‑message tests via .invoke() ===")
    text_cases = [
        "Patient has had a fever and cough for 4 days.",
        "No notable symptoms.",
        "Complains of diarrhea for 1 day and shortness of breath."
    ]
    for txt in text_cases:
        out = collect_symptoms(text_message=txt)
        print(f"\nINPUT TEXT: {txt!r}\nOUTPUT: {out}")

    # ─── Audio‑clip tests ─────────────────────────────────────────────────────────
    print("\n=== Audio‑clip tests via .invoke() ===")
    sample_dir = "/home/commanderzer0/Desktop/pocketclinic/tests/audio_samples"
    if not os.path.isdir(sample_dir):
        print(f"Directory '{sample_dir}' not found. Create it and drop in your audio files (wav/mp3/etc.).")
        return

    for fname in sorted(os.listdir(sample_dir)):
        if not fname.lower().endswith((".wav", ".mp3", ".m4a", ".mp4", ".webm", ".mpga", ".mpeg")):
            continue
        path = os.path.join(sample_dir, fname)
        with open(path, "rb") as f:
            audio_bytes = f.read()
        out = collect_symptoms(audio_clip=audio_bytes)
        print(f"\nFILE: {fname}\nOUTPUT: {out}")

if __name__ == "__main__":
    main()