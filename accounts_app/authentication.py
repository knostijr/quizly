"""
Custom authentication for JWT via cookies.
"""

from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that reads token from cookies.

    Extends JWTAuthentication to support HTTP-ONLY cookies
    instead of Authorization header.
    """

    def authenticate(self, request):
        """
        Authenticate request using JWT from cookie.

        Args:
            request: HTTP request with access_token cookie

        Returns:
            tuple: (user, token) if authentication successful
            None: If no token found

        Raises:
            AuthenticationFailed: If token is invalid
        """
        raw_token = request.COOKIES.get('access_token')

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        return self.get_user(validated_token), validated_token
