from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response

from engine.models import Community
from homelinked.models import HomePlans, HomepageNewFeature
from homelinked.serializers import HomePlansAPIViewSerializer, HomepageNewFeatureViewSerializer, \
    CommunitiesViewSerializer


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


class CommunitiesView(generics.ListAPIView):

    serializer_class = CommunitiesViewSerializer

    def get_queryset(self):
        return Community.objects.all()