from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response

from homelinked.models import HomePlans, HomepageNewFeature
from homelinked.serializers import HomePlansAPIViewSerializer, HomepageNewFeatureViewSerializer


# Create your views here.


class HomePlansAPIView(generics.ListCreateAPIView):
    serializer_class = HomePlansAPIViewSerializer

    def get_queryset(self):
        return HomePlans.objects.all()

class HomepageNewFeatureView(generics.ListAPIView):
    serializer_class = HomepageNewFeatureViewSerializer

    def get_queryset(self):
        return HomepageNewFeature.objects.filter(is_active=True).last()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset:
            serializer = self.get_serializer(queryset)
            return Response(serializer.data)
        return Response({"error": "please content on admin for homepage"})