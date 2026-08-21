from rest_framework import serializers

class EmailVerificationConfirmSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, min_length=6)

class GoogleAuthSerializer(serializers.Serializer):
    id_token = serializers.CharField()

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()



