"""
Utility functions for quiz generation pipeline.

These functions handle:
- YouTube video download and audio extraction
- Audio transcription using Whisper AI
- Quiz generation using Gemini Flash AI

Note: These are helper functions, not views.
"""

import os
import json
import yt_dlp
import whisper
from django.conf import settings
import google.generativeai as genai


def download_audio_from_youtube(video_url, max_duration_minutes=15):
    """
    Download YouTube video and extract audio as MP3.
    
    Uses yt-dlp to download video and ffmpeg to extract audio.
    Audio is saved to media/audio/ directory.
    
    Args:
        video_url (str): YouTube video URL
        max_duration_minutes (int): Maximum allowed video duration in minutes
    
    Returns:
        str: Path to downloaded MP3 file
    
    Raises:
        ValueError: If video exceeds max duration
        Exception: If download fails
    """
    # Check video duration first
    ydl_opts = {'quiet': True, 'no_warnings': True}
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        duration_seconds = info.get('duration', 0)
        duration_minutes = duration_seconds / 60
        
        if duration_minutes > max_duration_minutes:
            raise ValueError(
                f"Video zu lang! ({duration_minutes:.1f} Min). "
                f"Maximal {max_duration_minutes} Minuten erlaubt."
            )
    
    # Create directory
    os.makedirs('media/audio', exist_ok=True)
    
    # Download with ffmpeg extraction
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'media/audio/%(id)s.%(ext)s',
        'quiet': False,  # Show output for debugging
        'no_warnings': False,
        'ffmpeg_location': r'C:\ffmpeg\bin',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        video_id = info['id']
        audio_file = os.path.abspath(f"media/audio/{video_id}.mp3")
    
    # Verify file exists
    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"Audio file not created: {audio_file}")
    
    return audio_file


def get_youtube_video_title(video_url):
    """
    Get the title of a YouTube video without downloading.
    
    Uses yt-dlp to extract video metadata.
    Useful for creating quiz titles.
    
    Args:
        video_url (str): YouTube video URL
    
    Returns:
        str: Video title
    """
    ydl_opts = {'quiet': True, 'no_warnings': True}
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        title = info.get('title', 'Unknown Title')
    
    return title


def transcribe_audio_with_whisper(audio_file_path):
    """
    Transcribe audio file to text using Whisper AI.
    
    Uses OpenAI Whisper model to convert speech to text.
    Deletes audio file after transcription to save space.
    
    Args:
        audio_file_path (str): Path to MP3 audio file
    
    Returns:
        str: Transcribed text
    """
    # Convert to absolute path
    audio_file_path = os.path.abspath(audio_file_path)
    
    # Verify file exists before transcription
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
    
    # Load Whisper model
    model = whisper.load_model("base")
    
    # Transcribe audio
    result = model.transcribe(audio_file_path)
    transcript = result["text"]
    
    # Delete audio file to save disk space
    if os.path.exists(audio_file_path):
        os.remove(audio_file_path)
    
    return transcript


def generate_quiz_with_gemini(transcript, video_title=None):
    """
    Generate a quiz with 10 questions from transcript using Gemini AI.
    
    Uses Gemini Flash to create multiple-choice questions.
    Returns structured quiz data ready for database storage.
    
    Args:
        transcript (str): Video transcript text
        video_title (str, optional): Video title for quiz title
    
    Returns:
        dict: Quiz data with title, description, and 10 questions
    """
    # Configure Gemini
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Create prompt
    prompt = _create_quiz_prompt(transcript, video_title)
    
    # Generate quiz
    response = model.generate_content(prompt)
    
    # Parse JSON response
    quiz_text = response.text.strip()
    
    # Remove markdown code blocks if present
    if quiz_text.startswith('```json'):
        quiz_text = quiz_text[7:]
    if quiz_text.startswith('```'):
        quiz_text = quiz_text[3:]
    if quiz_text.endswith('```'):
        quiz_text = quiz_text[:-3]
    
    quiz_data = json.loads(quiz_text.strip())
    
    # Validate quiz data
    _validate_quiz_data(quiz_data)
    
    return quiz_data


def _create_quiz_prompt(transcript, video_title=None):
    """
    Create Gemini prompt for quiz generation.
    
    Internal helper function to build the prompt.
    
    Args:
        transcript (str): Video transcript
        video_title (str, optional): Video title
    
    Returns:
        str: Formatted prompt for Gemini
    """
    title_context = f"Video Title: {video_title}\n\n" if video_title else ""
    
    prompt = f"""
{title_context}Transcript:
{transcript}

---

Based on the above transcript, create a quiz with EXACTLY 10 multiple-choice questions.

REQUIREMENTS:
- Questions must test understanding of the main concepts
- Each question has 4 answer options (A, B, C, D)
- Only ONE correct answer per question
- Mix of difficulty levels (easy, medium, hard)
- Clear and unambiguous questions

OUTPUT FORMAT (JSON):
{{
  "title": "Quiz Title (based on content)",
  "description": "Brief description of quiz topic",
  "questions": [
    {{
      "question_title": "Question text here?",
      "question_options": {{
        "A": "First option",
        "B": "Second option",
        "C": "Third option",
        "D": "Fourth option"
      }},
      "answer": "A"
    }}
  ]
}}

IMPORTANT:
- Return ONLY valid JSON
- No markdown formatting
- No explanations outside JSON
- Exactly 10 questions
- Answer must be one of: A, B, C, D
"""
    
    return prompt


def _validate_quiz_data(quiz_data):
    """
    Validate quiz data structure and content.
    
    Internal helper function to ensure quiz data is valid.
    
    Args:
        quiz_data (dict): Quiz data from Gemini
    
    Raises:
        ValueError: If quiz data is invalid
    """
    # Check required fields
    if 'title' not in quiz_data:
        raise ValueError("Quiz data missing 'title'")
    
    if 'questions' not in quiz_data:
        raise ValueError("Quiz data missing 'questions'")
    
    questions = quiz_data['questions']
    
    # Check question count
    if len(questions) != 10:
        raise ValueError(f"Expected 10 questions, got {len(questions)}")
    
    # Validate each question
    for i, q in enumerate(questions):
        if 'question_title' not in q:
            raise ValueError(f"Question {i+1} missing 'question_title'")
        
        if 'question_options' not in q:
            raise ValueError(f"Question {i+1} missing 'question_options'")
        
        if 'answer' not in q:
            raise ValueError(f"Question {i+1} missing 'answer'")
        
        options = q['question_options']
        
        # Check all options present
        required_options = ['A', 'B', 'C', 'D']
        for opt in required_options:
            if opt not in options:
                raise ValueError(f"Question {i+1} missing option {opt}")
        
        # Check answer is valid
        if q['answer'] not in required_options:
            raise ValueError(
                f"Question {i+1} answer '{q['answer']}' "
                f"must be one of: {required_options}"
            )