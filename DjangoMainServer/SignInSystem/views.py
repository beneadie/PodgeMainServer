from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
#from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


from rest_framework.authtoken.models import Token

from .serializers import UserSerializer#, DeleteAccountSerializer, ChangePasswordSerializer

from rest_framework.views import APIView

from django.contrib.auth.models import update_last_login

#import time
User = get_user_model()

@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data) #json data input defined in serilizer.py
    if len(request.data['username']) > 32:
        return Response("Username is too long. Max 32 characters.", status=status.HTTP_400_BAD_REQUEST)
    if serializer.is_valid(): # if the data is valid it will save it
        serializer.save()
        #user = User.objects.get(username=request.data['username']) # NEED TO MAKE THIS WORJ WITH EMAIL VALIDATION
        user = User.objects.get(username=request.data['username'])
        user.set_password(request.data['password']) # hashes the password so not stred in plain text
        user.save()
        token = Token.objects.create(user=user)
        return Response({'token': token.key, 'user': serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) # should this be 400 error???

@api_view(['POST'])
def login(request):
    #user = get_object_or_404(User, email=request.data['email'])
    user = get_object_or_404(User, username=request.data['username'])
    if not user.check_password(request.data['password']):
        #time.sleep(1.5) maybe add this to prevent hackers if you know it wont slow the server for everyone
        return Response("missing user", status=status.HTTP_404_NOT_FOUND)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(user)
    return Response({'token': token.key, 'user': serializer.data})

# tests whether the user is currentyl logged in
@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response("passed for {}".format(request.user.username))

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    request.user.auth_token.delete()  # Invalidate the user's token
    return Response("Logged out successfully", status=status.HTTP_200_OK)



"""change password"""
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request):
    #serializer = UserSerializer(data=request.data)
    #serializer.is_valid(raise_exception=True)

    username = request.data.get('username')
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')

    # Check if the username is provided
    if not username:
        return Response({'error': 'Username is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Find the user by username
    user = get_object_or_404(User, username=username)

    # Verify that the authenticated user is the one changing their password
    if request.user != user:
        return Response({'error': 'You are not authorized to change this password.'}, status=status.HTTP_403_FORBIDDEN)

    # Validate the old password
    if not user.check_password(old_password):
        return Response({'error': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

    # Set the new password
    #note that you need to have token authenticated to do this in drf decorators
    user.set_password(new_password) #note that you need to have token authenticated to do this in drf decorators
    user.save()

    # Invalidate the old token and generate a new one
    Token.objects.filter(user=user).delete()  # Remove old token
    """decided it was better to log out the user after changing password
    It makes sure that nobody is logged in on other accounts with the old token and reduces complexity on the frontend
    """
    #token = Token.objects.create(user=user)    # Create a new token
    return Response({'message': 'Password changed successfully, Authentication Token Deleted'}, status=status.HTTP_200_OK)


"""
delete account
chose to not use serializer for this and change password.
"""
@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_account(request):
    username = request.data.get('username')
    user_password = request.data.get('user_password')
    # Check if the username is provided
    if not username:
        return Response({'error': 'Username is required.'}, status=status.HTTP_400_BAD_REQUEST)
    # Find the user by username in the model
    user = get_object_or_404(User, username=username)

    if not user.check_password(user_password):
        return Response({'error': 'password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
    Token.objects.filter(user=user).delete()
    user.delete()
    return Response({'message': 'User Deleted'}, status=status.HTTP_200_OK)

