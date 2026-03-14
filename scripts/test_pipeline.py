"""
Test complete quiz generation pipeline.

Tests the full flow:
1. YouTube URL → Audio Download
2. Audio → Whisper Transcription
3. Transcript → Gemini Quiz Generation
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

# Import utils (after Django setup!)
from quiz_app.utils import (
    download_audio_from_youtube,
    transcribe_audio_with_whisper,
    get_youtube_video_title
)


def test_pipeline():
    """Test the complete pipeline with a real YouTube video."""
    
    # Use a SHORT test video (2-3 minutes max!)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll (3:33 min)
    
    print("Testing complete quiz generation pipeline...")
    print(f"Video URL: {test_url}\n")
    
    try:
        # Step 1: Get title
        print("Getting video title...")
        title = get_youtube_video_title(test_url)
        print(f"Title: {title}\n")
        
        # Step 2: Download audio
        print("Downloading audio from YouTube...")
        audio_path = download_audio_from_youtube(test_url)
        print(f"Audio saved: {audio_path}\n")
        
        # Step 3: Transcribe
        print("Transcribing with Whisper (this takes a while)...")
        transcript = transcribe_audio_with_whisper(audio_path)
        print(f"Transcript ({len(transcript)} chars):")
        print(f"   {transcript[:200]}...\n")
            
        print("Pipeline test complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_pipeline()