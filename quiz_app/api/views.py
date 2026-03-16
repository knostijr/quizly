"""
API views for quiz management.
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from quiz_app.models import Quiz, Question
from .serializers import (
    QuizSerializer,
    QuizCreateSerializer
)
from quiz_app.utils import (
    download_audio_from_youtube,
    transcribe_audio_with_whisper,
    generate_quiz_with_gemini
)


class QuizViewSet(viewsets.ModelViewSet):
    """
    ViewSet for quiz CRUD operations.

    create:   POST /api/quizzes/ - Create quiz from YouTube URL
    list:     GET /api/quizzes/ - List user's quizzes
    retrieve: GET /api/quizzes/{id}/ - Get specific quiz
    update:   PATCH /api/quizzes/{id}/ - Update title/description
    destroy:  DELETE /api/quizzes/{id}/ - Delete quiz

    Permissions:
        All actions require authentication.
        Users can only access their own quizzes.
    """

    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Get quizzes for authenticated user only.

        Returns:
            QuerySet: User's quizzes with prefetched questions
        """
        return Quiz.objects.filter(
            user=self.request.user
        ).prefetch_related('questions')

    def create(self, request):
        """
        Create quiz from YouTube URL.

        Pipeline:
        1. Validate URL
        2. Download audio (yt_dlp)
        3. Transcribe audio (Whisper AI)
        4. Generate quiz (Gemini Flash)
        5. Save quiz and questions to database

        Args:
            request: HTTP request with {"url": "..."}

        Returns:
            Response: Created quiz with 10 questions

        Note:
            This operation takes 30-60 seconds.
            Frontend should show loading indicator.
        """
        serializer = QuizCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        video_url = serializer.validated_data['url']

        try:
            audio_file = download_audio_from_youtube(video_url)

            transcript = transcribe_audio_with_whisper(audio_file)

            quiz_data = generate_quiz_with_gemini(transcript)

            quiz = Quiz.objects.create(
                user=request.user,
                title=quiz_data['title'],
                description=quiz_data['description'],
                video_url=video_url
            )

            for question_data in quiz_data['questions']:
                Question.objects.create(
                    quiz=quiz,
                    question_title=question_data['question_title'],
                    question_options=question_data['question_options'],
                    answer=question_data['answer']
                )

            return Response(
                QuizSerializer(quiz).data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response({
                "detail": f"Quiz creation failed: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        """
        Update quiz title and/or description only.

        Args:
            request: HTTP request with title/description
            pk: Quiz ID

        Returns:
            Response: Updated quiz data
        """
        quiz = self.get_object()

        allowed_fields = ['title', 'description']
        data = {
            k: v for k, v in request.data.items()
            if k in allowed_fields
        }

        serializer = self.get_serializer(
            quiz,
            data=data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
