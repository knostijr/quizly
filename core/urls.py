"""
Main URL configuration for quizly project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts_app.api.urls')),
    path('api/', include('quiz_app.api.urls')),
]