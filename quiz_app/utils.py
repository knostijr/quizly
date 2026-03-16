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
    _validate_video_duration(video_url, max_duration_minutes)
    return _download_and_extract_audio(video_url)


def _validate_video_duration(video_url, max_duration_minutes):
    """
    Check if video duration is within allowed limit.

    Args:
        video_url (str): YouTube video URL
        max_duration_minutes (int): Maximum allowed duration

    Raises:
        ValueError: If video exceeds max duration
    """
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


def _download_and_extract_audio(video_url):
    """
    Download video and extract audio as MP3.

    Args:
        video_url (str): YouTube video URL

    Returns:
        str: Absolute path to downloaded MP3 file

    Raises:
        FileNotFoundError: If audio file not created
    """
    os.makedirs('media/audio', exist_ok=True)
    ydl_opts = _get_ytdlp_options()
    audio_file = _execute_download(video_url, ydl_opts)
    return audio_file


def _get_ytdlp_options():
    """
    Get yt-dlp configuration for audio extraction.

    Returns:
        dict: yt-dlp options for MP3 extraction
    """
    return {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'media/audio/%(id)s.%(ext)s',
        'quiet': False,
        'no_warnings': False,
        'ffmpeg_location': r'C:\ffmpeg\bin',
    }


def _execute_download(video_url, ydl_opts):
    """
    Execute video download and return audio file path.

    Args:
        video_url (str): YouTube video URL
        ydl_opts (dict): yt-dlp options

    Returns:
        str: Absolute path to MP3 file

    Raises:
        FileNotFoundError: If audio file not created
    """
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        video_id = info['id']
        audio_file = os.path.abspath(f"media/audio/{video_id}.mp3")

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
    audio_file_path = os.path.abspath(audio_file_path)

    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

    model = whisper.load_model("base")
    result = model.transcribe(audio_file_path)
    transcript = result["text"]

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
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')

    prompt = _create_quiz_prompt(transcript, video_title)
    response = model.generate_content(prompt)

    quiz_text = response.text.strip()
    quiz_text = _remove_markdown_formatting(quiz_text)
    quiz_data = json.loads(quiz_text.strip())

    _validate_quiz_data(quiz_data)
    return quiz_data


def _remove_markdown_formatting(text):
    """
    Remove markdown code block formatting from text.

    Args:
        text (str): Text potentially containing markdown

    Returns:
        str: Text without markdown formatting
    """
    if text.startswith('```json'):
        text = text[7:]
    if text.startswith('```'):
        text = text[3:]
    if text.endswith('```'):
        text = text[:-3]
    return text


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
    _validate_quiz_structure(quiz_data)
    _validate_all_questions(quiz_data['questions'])


def _validate_quiz_structure(quiz_data):
    """
    Validate quiz has required fields and correct question count.

    Args:
        quiz_data (dict): Quiz data to validate

    Raises:
        ValueError: If structure is invalid
    """
    if 'title' not in quiz_data:
        raise ValueError("Quiz data missing 'title'")

    if 'questions' not in quiz_data:
        raise ValueError("Quiz data missing 'questions'")

    questions = quiz_data['questions']
    if len(questions) != 10:
        raise ValueError(f"Expected 10 questions, got {len(questions)}")


def _validate_all_questions(questions):
    """
    Validate each question has correct format and options.

    Args:
        questions (list): List of question dictionaries

    Raises:
        ValueError: If any question is invalid
    """
    for i, q in enumerate(questions):
        _validate_single_question(q, i + 1)


def _validate_single_question(question, question_number):
    """
    Validate a single question's structure and content.

    Args:
        question (dict): Question data
        question_number (int): Question number for error messages

    Raises:
        ValueError: If question is invalid
    """
    if 'question_title' not in question:
        raise ValueError(
            f"Question {question_number} missing 'question_title'")

    if 'question_options' not in question:
        raise ValueError(
            f"Question {question_number} missing 'question_options'")

    if 'answer' not in question:
        raise ValueError(f"Question {question_number} missing 'answer'")

    _validate_question_options(question, question_number)


def _validate_question_options(question, question_number):
    """
    Validate question has all required options and valid answer.

    Args:
        question (dict): Question data
        question_number (int): Question number for error messages

    Raises:
        ValueError: If options or answer are invalid
    """
    options = question['question_options']
    required_options = ['A', 'B', 'C', 'D']

    for opt in required_options:
        if opt not in options:
            raise ValueError(
                f"Question {question_number} missing option {opt}")

    if question['answer'] not in required_options:
        raise ValueError(
            f"Question {question_number} answer '{question['answer']}' "
            f"must be one of: {required_options}"
        )
