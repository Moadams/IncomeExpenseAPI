import jwt

from django.shortcuts import render
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status 
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer 
from .models import User
from .utils import Util


# Create your views here.

class RegisterView(generics.GenericAPIView):

    serializer_class = RegisterSerializer

    def post(self, request):
        user = request.data
        serializer = RegisterSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data

        user = User.objects.get(email=user_data['email'])
        token = RefreshToken.for_user(user).access_token

        current_site = get_current_site(request)
        relative_link = reverse("email-verify")
        absurl = f'http://{current_site}{relative_link}?token={str(token)}'
        email_body = f'Hi, {user.username}, use the link below to verify your email. \n{absurl}'
        data = {
            "domain":current_site.domain,
            "email_subject":"Verify your email",
            "email_body":email_body,
            "link":absurl,
            "to_email": user.email
        }

        if not Util.send_email(data):
            user.delete()
        return Response(user_data, status=status.HTTP_201_CREATED)


class VerifyEmail(generics.GenericAPIView):
    def get(self, request):
        token = request.GET.get('token',None)
        print(token)
        try:
            payload = jwt.decode(token,settings.SECRET_KEY)
            print(payload)
            user = User.objects.get(id = payload['user_id'])
            
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response({"email":"Successfully activated"}, status=status.HTTP_200_OK)
            
        except jwt.ExpiredSignatureError as identifier:
            return Response({"error":"Activation Link Expired"}, status=status.HTTP_400_BAD_REQUEST)

        except jwt.exceptions.DecodeError as identifier:
            return Response({"error":"Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as identifier:
            return Response({"error":"Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)