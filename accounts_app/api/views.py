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
        

class LoginView(APIView):
    """
    API endpoint for user login with JWT cookies.
    
    POST /api/login/
    
    Request body:
        username: str
        password: str
    
    Response:
        200: Login successful, sets HTTP-ONLY cookies
        401: Invalid credentials
    
    Cookies set:
        access_token: JWT access token (15 minutes)
        refresh_token: JWT refresh token (7 days)
    """
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Authenticate user and set JWT cookies.
        
        Args:
            request: HTTP request with credentials
        
        Returns:
            Response: Login success with user data and HTTP-ONLY cookies
        """
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response({
                "detail": "Invalid credentials"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        response = Response({
            "detail": "Login successfully!",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }, status=status.HTTP_200_OK)
        
        # Set access_token cookie (HTTP-ONLY!)
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=60 * 15  # 15 minutes
        )
        
        # Set refresh_token cookie (HTTP-ONLY!)
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=60 * 60 * 24 * 7  # 7 days
        )
        
        return response