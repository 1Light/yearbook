from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class StudentReunionSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    reunion_date = serializers.DateTimeField()