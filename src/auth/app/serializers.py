from rest_framework import serializers

from app.models import User

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(allow_null=False, allow_blank=False)
    password = serializers.CharField(allow_null=False, allow_blank=False)

    def validate(self, attrs):
        if not attrs['email'] or not attrs['password']:
            raise serializers.ValidationError('Missing Credentials')
        
        try:
            user = User.objects.get(email=attrs['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid Credentials')

        if user.check_password(attrs['password']):
            attrs['user'] = user
        else:
            serializers.ValidationError("Invalid Credentials")
        
        return attrs