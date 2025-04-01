from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    class Meta:
        model = User
        fields = ['email', 'username', 'password']

    def validate(self, attrs):
        email = attrs.get('email', '')
        username = attrs.get('username', '')

        if not username.isalnum(): # check if the username contains only alphanumeric characters
            raise serializers.ValidationError("Username should only contain alphanumeric characters")

        return attrs
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)