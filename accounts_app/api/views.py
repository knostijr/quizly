"""
API views for user authentication.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .serializers import RegisterSerializer


class RegisterView(APIView):
    """
    API endpoint for user registration.
    
    POST /api/register/
    
    Request body:
        username: str
        email: str
        password: str
        confirmed_password: str
    
    Response:
        201: User created successfully
        400: Invalid data
    """
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Register new user.
        
        Args:
            request: HTTP request with user data
        
        Returns:
            Response: Success message or validation errors
        """
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            
            return Response({
                "detail": "User created successfully!"
            }, status=status.HTTP_201_CREATED)
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )