from django.shortcuts import render
from rest_framework import generics
from rest_auth.registration.views import RegisterView
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import models
from . import serializers

# Create your views here.

class AdminUserList(generics.ListAPIView):
    queryset = models.AdminUser.objects.all()
    serializer_class = serializers.AdminUserSerializer


class AdminUserRegister(RegisterView):
    serializer_class = serializers.RegisterAdminUserSerializer

@api_view
def null_view(request):
    return Response(status=status.HTTP_400_BAD_REQUEST)


