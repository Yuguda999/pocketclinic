#!/usr/bin/env python3
import sys
import os
import requests
import json
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Base URL for API
BASE_URL = "http://localhost:8000/api/v1"

def test_text_process():
    """Test the text process endpoint"""
    print("\n=== Testing Text Process Endpoint ===")
    
    # Test data
    data = {
        "text_message": "Patient has had a fever and cough for 4 days with difficulty breathing.",
        "phone_number": "+2348012345678"
    }
    
    # Send request
    response = requests.post(f"{BASE_URL}/process", json=data)
    
    # Print results
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.json()

def test_audio_process():
    """Test the audio process endpoint"""
    print("\n=== Testing Audio Process Endpoint ===")
    
    # Find an audio sample
    sample_dir = Path(__file__).parent / "audio_samples"
    if not sample_dir.exists():
        print(f"Directory '{sample_dir}' not found. Create it and drop in your audio files (wav/mp3/etc.).")
        return None
    
    # Get the first audio file
    audio_files = list(sample_dir.glob("*.wav")) + list(sample_dir.glob("*.mp3"))
    if not audio_files:
        print(f"No audio files found in '{sample_dir}'. Add some audio files for testing.")
        return None
    
    audio_file = audio_files[0]
    print(f"Using audio file: {audio_file}")
    
    # Prepare form data
    files = {
        "audio_file": (audio_file.name, open(audio_file, "rb"), f"audio/{audio_file.suffix[1:]}")
    }
    data = {
        "phone_number": "+2348012345678"
    }
    
    # Send request
    response = requests.post(f"{BASE_URL}/process/audio", files=files, data=data)
    
    # Print results
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.json()

if __name__ == "__main__":
    print("=== PocketClinic API Tests (Single Endpoint) ===")
    
    # Test endpoints
    test_text_process()
    test_audio_process()
