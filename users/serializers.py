from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password']
        extra_kwargs = {'password': {'write_only': True}}
        
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(email=validated_data['email'])
        user.set_password(password)
        user.save()
        return user
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
