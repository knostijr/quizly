"""
Serializers for quiz API endpoints.
"""

from rest_framework import serializers
from quiz_app.models import Quiz, Question


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for Question model.

    Read-only serializer for questions within quiz.
    Questions are created via quiz creation pipeline.
    """

    class Meta:
        model = Question
        fields = [
            'id',
            'question_title',
            'question_options',
            'answer',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class QuizSerializer(serializers.ModelSerializer):
    """
    Serializer for Quiz model with nested questions.

    Used for list, retrieve, and update operations.
    Questions are included as nested read-only data.
    """

    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            'id',
            'title',
            'description',
            'created_at',
            'updated_at',
            'video_url',
            'questions'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class QuizCreateSerializer(serializers.Serializer):
    """
    Serializer for creating quiz from YouTube URL.

    Only accepts URL, quiz generation happens in view.

    Fields:
        url: YouTube video URL
    """

    url = serializers.URLField(
        required=True,
        help_text="YouTube video URL"
    )

    def validate_url(self, value):
        """
        Validate that URL is a YouTube link.

        Args:
            value (str): YouTube URL

        Returns:
            str: Validated URL

        Raises:
            ValidationError: If URL is not YouTube
        """
        if 'youtube.com' not in value and 'youtu.be' not in value:
            raise serializers.ValidationError(
                "URL must be a valid YouTube link"
            )
        return value
