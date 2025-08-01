# accounts/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import CustomUser
from .models import UserToken
from .utils import get_device_name_from_request
from django.db import transaction
from django.utils import timezone




class RegisterUser(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        required_fields = ['username', 'password', 'email', 'phone', 'whatsapp']
        if not all(field in data for field in required_fields):
            return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(username=data['username']).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(email=data['email']).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(phone=data['phone']).exists():
            return Response({'error': 'Phone already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.create_user(
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            username=data['username'],
            password=data['password'],
            email=data['email'],
            phone=data['phone'],
            whatsapp=data['whatsapp'],
            is_admin=data.get('is_admin', False)
        )

        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)


# class LoginUser(APIView):
#     permission_classes = [AllowAny]
#
#     def post(self, request):
#         username = request.data.get('username')
#         password = request.data.get('password')
#
#         user = authenticate(username=username, password=password)
#         if user is not None:
#             token, _ = Token.objects.get_or_create(user=user)
#             return Response({'token': token.key, 'is_admin': user.is_admin})
#         else:
#             return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)



# class LogoutUser(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request):
#         request.user.auth_token.delete()
#         return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)


class LoginUser(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        # Auto-detect device name
        device_name = request.data.get('device_name') or get_device_name_from_request(request) or 'Unknown Device'

        # Capture IP & raw UA (for auditing)
        xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
        ip = (xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR'))
        raw_ua = request.META.get('HTTP_USER_AGENT', '')

        # 1️⃣ Check if a token already exists for this device name
        existing_token = user.auth_tokens.filter(name=device_name).first()
        if existing_token:
            # Update IP, UA, and last_used (optional)
            existing_token.ip = ip
            existing_token.user_agent = raw_ua
            existing_token.last_used = timezone.now()
            existing_token.save(update_fields=['ip', 'user_agent', 'last_used'])
            return Response({
                'token': existing_token.key,
                'device_name': existing_token.name,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'is_admin': getattr(user, 'is_admin', False),
                },
                'created': existing_token.created,
            }, status=status.HTTP_200_OK)

        # 2️⃣ Enforce max 3 tokens
        tokens_qs = user.auth_tokens.order_by('-created')  # newest first
        MAX_ACTIVE_TOKENS = 3
        # if tokens_qs.count() >= MAX_ACTIVE_TOKENS:
        #     tokens_qs.last().delete()  # delete oldest
        if tokens_qs.count() >= MAX_ACTIVE_TOKENS:
            return Response({'error': 'Maximum active devices reached (3). Logout another device first.'},
                            status=status.HTTP_403_FORBIDDEN)

        # 3️⃣ Create a new token only if no existing token for this device
        token = UserToken.objects.create(
            user=user,
            name=device_name,
            ip=ip,
            user_agent=raw_ua,
        )

        return Response({
            'token': token.key,
            'device_name': token.name,
            'user': {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'is_admin': getattr(user, 'is_admin', False),
            },
            'created': token.created,
        }, status=status.HTTP_200_OK)



class LogoutUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Logout only the CURRENT device: delete the token used in this request.
        request.auth is the UserToken instance returned by the custom auth.
        """
        token = getattr(request, 'auth', None)
        if token is None:
            return Response({'message': 'No token found on this request.'}, status=status.HTTP_200_OK)

        token.delete()
        return Response({'message': 'Logged out from this device.'}, status=status.HTTP_200_OK)