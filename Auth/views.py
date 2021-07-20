import datetime

import jwt
from rest_framework.decorators import api_view
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response

from .models import User
from .serializers import UserSerializer, RegisterSerializer, ProfileSerializer


def GetUser(request, required=True):
    token = request.META.get('HTTP_TOKEN')
    payload = {}
    expired = False
    if not token and required:
        raise AuthenticationFailed("UnAuthenticated")
    try:
        if token:
            payload = jwt.decode(token, "secret", algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        expired = True
        if required:
            raise AuthenticationFailed("UnAuthenticated")
    if token and not expired:
        user = User.objects.get(id=payload['id'])
        return user
    return None


@api_view(['GET'])
def BaseAPI(request):
    paths = {
        'Users List': '/users',
        'User Detail': '/user/<id>',
        "Login": "/login",
        "Register": '/register',
        'Logout': '/logout'
    }
    return Response(paths)


@api_view(['GET'])
def UsersList(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def UserDetail(request, pk):
    user = User.objects.get(id=pk)
    serializer = UserSerializer(user)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
def UserCreate(request):
    if request.method == "POST":
        request.data._mutable = True
        password = request.data['password']
        password2 = request.data['password2']
        if password != password2:
            return Response({"response": "Password doesn't Match"})
        request.data['password'] = password
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(username=request.data['username'])
            user.set_password(password)
            user.save()
            payload = {
                'id': user.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30),
                'iat': datetime.datetime.utcnow()
            }

            token = jwt.encode(payload, 'secret', algorithm='HS256')
            response = Response(status=200)
            # response.set_cookie(key='jwt', value=token, httponly=True)
            response.data = {
                'jwt': token
            }
            return response
        else:
            for key, values in serializer.errors.items():
                error = [value[:] for value in values]
                return Response({"response": error[0]})
    return Response("Register")


@api_view(["GET", "POST"])
def UserLogin(request):
    if request.method == "POST":
        print("token", request.META.get('HTTP_TOKEN'))
        username = request.data['username']
        password = request.data['password']
        user = User.objects.filter(username=username).first()

        if user is None:
            return Response({"response": "Invalid Credentials"})

        if not user.check_password(password):
            return Response({"response": "Invalid Credentials"})

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')
        response = Response(status=200)
        # response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }
        return response
    return Response("Login")


@api_view(["GET", "POST"])
def UserProfile(request):
    token = request.META.get('HTTP_TOKEN')
    print(token)
    user = GetUser(request)
    print(user)
    if request.method == "GET":
        user = User.objects.get(id=user.id)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    if request.method == "POST":
        if 'image' in request.data:
            user.image = request.data.get('image', user.image)
            user.save()
        else:
            first_name = request.data.get('first_name', user.first_name)
            last_name = request.data.get('last_name', user.last_name)
            email = request.data.get('email', user.email)
            username = request.data.get('username', user.username)
            serializer = ProfileSerializer(
                data={
                    'first_name': first_name,
                    'email': email,
                    'last_name': last_name,
                    'username': username,
                }, instance=user)
            if serializer.is_valid():
                serializer.save()
            else:
                for key, values in serializer.errors.items():
                    error = [value[:] for value in values]
                    return Response(error, status=400)
    return Response(UserSerializer(user).data)
