from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = CustomUser
        fields = ('email', 'name', 'password')

    def create(self, validated_data):
        return CustomUser.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
            role='User'
        )