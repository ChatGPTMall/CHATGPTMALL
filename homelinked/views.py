from django.shortcuts import render
from rest_framework import generics

from homelinked.models import HomePlans
from homelinked.serializers import HomePlansAPIViewSerializer


# Create your views here.


class HomePlansAPIView(generics.ListCreateAPIView):
    serializer_class = HomePlansAPIViewSerializer

    def get_queryset(self):
        return HomePlans.objects.all()