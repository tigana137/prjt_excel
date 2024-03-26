from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from users.functions import create_jwtResponse, verify_jwt
from users.models import UserProfile
from users.serializers import UserSerializer
from x.models import Dre
# Create your views here.
from django.shortcuts import get_object_or_404


@api_view(['GET'])
def testSignal(request):

    return Response(True)


@api_view(['POST'])
def verifyDreCredentials(request):

    if not 'dre_username' in request.data or not 'password' in request.data:
        return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)

    dre_username = request.data['dre_username']
    dre_password = request.data['password']

    dre = get_object_or_404(Dre, username=dre_username)

    if dre.password != dre_password:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    response = create_jwtResponse(dre_id=dre.id)

    return response


@api_view(['POST'])
def signup(request):

    jwt_payload = verify_jwt(request)

    dre_id = jwt_payload['dre_id']

    serializer = UserSerializer(data=request.data)

    if not serializer.is_valid() or not 'email' in serializer.validated_data:
        return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()
    user = User.objects.get(username=request.data['username'])
    user.set_password(request.data['password'])
    user.save()

    user_profile = UserProfile.objects.create(user=user, dre_id=dre_id)
    user_profile.save()

    return Response({'success': True, 'dre': user_profile.dre.name}, status=status.HTTP_200_OK)


@api_view(['POST'])
def signin(request):
    if not 'username' in request.data or not 'password' in request.data:
        return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)

    username = request.data['username']
    password = request.data['password']

    user = get_object_or_404(User, username=username)

    if not user.check_password(password):
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    response = create_jwtResponse(dre_id=user.userprofile.dre_id)

    return response



@api_view(['GET'])
def logout(request):
    response =Response()
    response.delete_cookie('jwt')
    response.data = {
        'success': True
    }

    return response

