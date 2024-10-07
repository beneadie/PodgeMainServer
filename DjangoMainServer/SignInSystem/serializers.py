from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

"""authentication serializer"""
class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'folder_id']

#"""change password serializer"""
#class ChangePasswordSerializer(serializers.Serializer):
#    old_password = serializers.CharField(required=True)
#    new_password = serializers.CharField(required=True)
#
#    def validate_old_password(self, value):
#        user = self.context['request'].username
#        if not user.check_password(value):
#            raise serializers.ValidationError("Old password is not correct.")
#        return value
#
#    def validate_new_password(self, value):
#        # Use Django's built-in password validators
#        validate_password(value)
#        return value
#
#"""delete account serializer"""
#class DeleteAccountSerializer(serializers.Serializer):
#    serializer = serializers.CharField(required=True)
#    def validate_password(self, value):
#        username = self.context['request'].username
#        if not serializer.check_password(value):
#            raise serializers.ValidationError("password is not correct.")
#        return value

