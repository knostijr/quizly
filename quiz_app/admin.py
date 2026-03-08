"""
Admin configuration for quiz application.
"""

from django.contrib import admin
from .models import Quiz, Question


class QuestionInline(admin.TabularInline):
    """
    Inline admin for questions within quiz admin.
    
    Allows editing questions directly in quiz detail view.
    """
    
    model = Question
    extra = 1
    fields = ['question_title', 'question_options', 'answer']
    
    # Limit to reasonable number of inlines
    max_num = 15


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """
    Admin configuration for Quiz model.
    
    Features:
    - List display with key fields
    - Filtering by creation date and user
    - Search by title and description
    - Inline question editing
    """
    
    list_display = [
        'title',
        'user',
        'created_at',
        'question_count',
        'video_url'
    ]
    list_filter = ['created_at', 'user']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [QuestionInline]
    
    def get_queryset(self, request):
        """Optimize queryset with prefetch_related."""
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('questions')
    
    def question_count(self, obj):
        """Display number of questions in list view."""
        return obj.questions.count()
    
    question_count.short_description = 'Questions'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    Admin configuration for Question model.
    
    Allows managing questions separately from quizzes.
    """
    
    list_display = [
        'question_title',
        'quiz',
        'answer',
        'created_at'
    ]
    list_filter = ['quiz', 'created_at']
    search_fields = ['question_title', 'answer']
    readonly_fields = ['created_at', 'updated_at']