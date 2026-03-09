"""
Serializers for user authentication.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    
    Validates username, email, and password match.
    Creates new user with hashed password.
    
    Fields:
        username: Unique username
        email: User email address
        password: User password (write-only)
        confirmed_password: Password confirmation (write-only)
    """
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    confirmed_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirmed_password']
    
    def validate(self, attrs):
        """
        Validate that passwords match.
        
        Args:
            attrs: Dictionary of field values
        
        Returns:
            attrs: Validated attributes
        
        Raises:
            ValidationError: If passwords don't match
        """
        if attrs['password'] != attrs['confirmed_password']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs
    
    def create(self, validated_data):
        """
        Create new user with hashed password.
        
        Args:
            validated_data: Validated data from serializer
        
        Returns:
            User: Created user instance
        """
        # Remove confirmed_password (not needed for user creation)
        validated_data.pop('confirmed_password')
        
        # Create user with hashed password
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        return user