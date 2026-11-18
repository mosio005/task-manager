from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()




class RegisterSerializer(serializers.ModelSerializer):

    password_2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'password_2'
        ]
        extra_kwargs = {
            'password':{'write_only':True}
        }

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'This email is already registered.'
            )
        return email

    def validate_password(self, password):
        if len(password) < 8:
            raise serializers.ValidationError(
                'the password must be atleast 8 chracter'
            )
        return password


    def validate(self, attrs):
        if attrs['password'] != attrs['password_2']:
            raise serializers.ValidationError(
                'password2 : Password fields did not match.'
            )

        return attrs


    def create(self, validated_data):
        validated_data.pop('password_2')
        user = User.objects.create_user(**validated_data)
        return user
    