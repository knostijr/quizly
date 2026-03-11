"""
Utility functions for quiz generation pipeline.

These functions handle:
- YouTube video download and audio extraction
- Audio transcription using Whisper AI
- Quiz generation using Gemini Flash AI

Note: These are helper functions, not views.
"""

import os
import yt_dlp
import whisper


def download_audio_from_youtube(video_url):
    """
    Download YouTube video and extract audio as MP3.
    
    Uses yt-dlp to download video and ffmpeg to extract audio.
    Audio is saved to media/audio/ directory.
    
    Args:
        video_url (str): YouTube video URL
    
    Returns:
        str: Path to downloaded MP3 file
    
    Raises:
        Exception: If download fails
    
    Example:
        audio_path = download_audio_from_youtube('https://youtube.com/watch?v=...')
        print(audio_path)
        'media/audio/dQw4w9WgXcQ.mp3'
    """
    # Ensure media/audio directory exists
    os.makedirs('media/audio', exist_ok=True)
    
    # yt-dlp options
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'media/audio/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }
    
    # Download and extract audio
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        audio_file = f"media/audio/{info['id']}.mp3"
    
    return audio_file

def transcribe_audio_with_whisper(audio_file_path):
    """
    Transcribe audio file to text using Whisper AI.
    
    Uses OpenAI Whisper model to convert speech to text.
    Deletes audio file after transcription to save space.
    
    Args:
        audio_file_path (str): Path to MP3 audio file
    
    Returns:
        str: Transcribed text
    
    Raises:
        Exception: If transcription fails
    
    Example:
        text = transcribe_audio_with_whisper('media/audio/video.mp3')
        print(text[:50])
        'Welcome to this video about how to make your own quizApp...'
    """
    # Load Whisper model (base = faster, small = better quality)
    # for testing we are using base
    # tiny, base, small, medium, large
    model = whisper.load_model("base")
    
    # Transcribe audio
    result = model.transcribe(audio_file_path)
    transcript = result["text"]
    
    # Delete audio file to save disk space
    if os.path.exists(audio_file_path):
        os.remove(audio_file_path)
    
    return transcript