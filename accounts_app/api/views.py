"""
API views for user authentication.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
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
            max_age=60 * 15
        )
        
        # Set refresh_token cookie (HTTP-ONLY!)
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=60 * 60 * 24 * 7
        )
        
        return response


class LogoutView(APIView):
    """
    API endpoint for user logout with token blacklist.
    
    POST /api/logout/
    
    Blacklists the refresh token and deletes cookies.
    User must login again to get new tokens.
    
    Response:
        200: Logout successful, tokens blacklisted
        400: Logout failed
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Logout user and blacklist refresh token.
        
        Args:
            request: HTTP request with refresh_token cookie
        
        Returns:
            Response: Logout success message
        """
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            response = Response({
                "detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."
            }, status=status.HTTP_200_OK)
            
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
            
            return response
            
        except TokenError as e:
            return Response({
                "detail": f"Logout failed: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "detail": f"Logout error: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)


class TokenRefreshView(APIView):
    """
    API endpoint for refreshing access token.
    
    POST /api/token/refresh/
    
    Reads refresh_token from cookie and generates new access_token.
    
    Response:
        200: New access token set in cookie
        401: Invalid or missing refresh token
    """
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Refresh access token using refresh token from cookie.
        
        Args:
            request: HTTP request with refresh_token cookie
        
        Returns:
            Response: New access token in cookie
        """
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not refresh_token:
            return Response({
                "detail": "Refresh token not found"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            token = RefreshToken(refresh_token)
            new_access_token = str(token.access_token)
            
            response = Response({
                "detail": "Token refreshed"
            }, status=status.HTTP_200_OK)
            
            # Set new access_token cookie
            response.set_cookie(
                key='access_token',
                value=new_access_token,
                httponly=True,
                secure=False,
                samesite='Lax',
                max_age=60 * 15
            )
            
            return response
            
        except TokenError:
            return Response({
                "detail": "Invalid refresh token"
            }, status=status.HTTP_401_UNAUTHORIZED)