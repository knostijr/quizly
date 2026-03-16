# 🎯 quizly - AI-Powered YouTube Quiz Generator

Generate quizzes automatically from YouTube videos using AI!

## Features

- **JWT Authentication** with HTTP-ONLY cookies
- **YouTube Video Processing** (yt-dlp)
- **AI Transcription** (Whisper AI)
- **AI Quiz Generation** (Gemini Flash)
- **10 questions per quiz** with 4 multiple-choice options
- **CRUD Operations** for quiz management
- **User Isolation** - users only see their own quizzes
- **Admin Panel** for quiz and question management

## ⚡ Requirements

### CRITICAL: FFMPEG Installation

**FFMPEG must be installed globally before running this project!**

FFMPEG is required for Whisper AI to process audio files.

#### Windows
1. Download: https://www.gyan.dev/ffmpeg/builds/
2. Extract to `C:\ffmpeg`
3. Add to PATH: `C:\ffmpeg\bin`
4. Verify: `ffmpeg -version`

#### macOS
```bash
brew install ffmpeg
ffmpeg -version
```

#### Linux
```bash
sudo apt update
sudo apt install ffmpeg
ffmpeg -version
```

## 🚀 Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd quizly_backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables
Copy `.env.template` to `.env` and fill in:
```env
SECRET_KEY=your-django-secret-key
DEBUG=True
GEMINI_API_KEY=your-gemini-api-key
```

**Get Gemini API Key:**
1. Visit: https://ai.google.dev/
2. Click "Get API Key"
3. Sign in with Google
4. Copy API key to `.env`

### 5. Database Setup
```bash
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Run Server
```bash
python manage.py runserver
```

Server runs at: http://127.0.0.1:8000

## 🔧 API Endpoints

### Authentication
- `POST /api/register/` - User registration
- `POST /api/login/` - Login (sets HTTP-ONLY cookies)
- `POST /api/logout/` - Logout (blacklists token)
- `POST /api/token/refresh/` - Refresh access token

### Quizzes
- `POST /api/quizzes/` - Create quiz from YouTube URL (30-60s)
- `GET /api/quizzes/` - List user's quizzes
- `GET /api/quizzes/{id}/` - Get specific quiz
- `PATCH /api/quizzes/{id}/` - Update title/description
- `DELETE /api/quizzes/{id}/` - Delete quiz

## 🧪 Testing

Run all tests:
```bash
python manage.py test
```

Run specific app tests:
```bash
python manage.py test accounts_app
python manage.py test quiz_app
```

## Security Features

- **HTTP-ONLY Cookies** - JavaScript cannot access tokens
- **Token Blacklist** - Invalidate tokens on logout
- **User Isolation** - Users only see own quizzes
- **JWT Expiration** - Access token: 15min, Refresh: 7 days

## AI Pipeline

1. **YouTube Download** (yt-dlp)
   - Downloads video
   - Extracts audio as MP3
   - Uses ffmpeg for conversion

2. **Transcription** (Whisper AI)
   - Converts audio to text
   - Uses Whisper base model
   - Deletes audio after transcription

3. **Quiz Generation** (Gemini Flash)
   - Analyzes transcript
   - Generates 10 questions
   - 4 options per question
   - Validates structure

## Configuration

### Development
```python
DEBUG = True
CORS_ALLOW_ALL_ORIGINS = True
```

### Production
```python
DEBUG = False
CORS_ALLOWED_ORIGINS = ['https://yourdomain.com']
SIMPLE_JWT['AUTH_COOKIE_SECURE'] = True
```

##  Tech Stack

- **Backend:** Django 4.2.7
- **API:** Django REST Framework 3.14.0
- **Auth:** SimpleJWT 5.3.0 (HTTP-ONLY cookies)
- **YouTube:** yt-dlp 2023.12.30
- **Transcription:** OpenAI Whisper
- **Quiz Generation:** Google Gemini Flash
- **Database:** SQLite (Development)

## Troubleshooting

### FFMPEG not found