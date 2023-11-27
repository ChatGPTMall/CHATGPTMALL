from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import filters
from engine.models import Community
from homelinked.models import HomePlans, HomepageNewFeature
from homelinked.serializers import HomePlansAPIViewSerializer, HomepageNewFeatureViewSerializer, \
    CommunitiesViewSerializer, GetCreditsHistorySerializer


# Create your views here.


class HomePlansAPIView(generics.ListCreateAPIView):
    swagger_schema = None
    serializer_class = HomePlansAPIViewSerializer

    def get_queryset(self):
        return HomePlans.objects.all()


class HomepageNewFeatureView(generics.ListAPIView):
    swagger_schema = None
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
    swagger_schema = None
    serializer_class = CommunitiesViewSerializer

    def get_queryset(self):
        return Community.objects.all()


class GetCreditsHistory(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetCreditsHistorySerializer

    def get_queryset(self):
        return self.request.user.credits_history.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
