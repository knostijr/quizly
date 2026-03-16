"""
Test complete quiz generation pipeline.

Tests the full flow:
1. YouTube URL → Audio Download
2. Audio → Whisper Transcription
3. Transcript → Gemini Quiz Generation
"""

from quiz_app.utils import (
    download_audio_from_youtube,
    transcribe_audio_with_whisper,
    get_youtube_video_title
)
import django
import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()


def test_pipeline():
    """Test the complete pipeline with a real YouTube video."""

    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    print("Testing complete quiz generation pipeline...")
    print(f"Video URL: {test_url}\n")

    try:
        print("Getting video title...")
        title = get_youtube_video_title(test_url)
        print(f"Title: {title}\n")

        print("Downloading audio from YouTube...")
        audio_path = download_audio_from_youtube(test_url)
        print(f"Audio saved: {audio_path}\n")

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
