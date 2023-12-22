from django.db.models import Count, Case, When, Value, BooleanField, Exists, OuterRef
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import filters
from engine.models import Community, CommunityMembers, Items
from homelinked.models import HomePlans, HomepageNewFeature
from homelinked.serializers import HomePlansAPIViewSerializer, HomepageNewFeatureViewSerializer, \
    CommunitiesViewSerializer, GetCreditsHistorySerializer, CommunitiesJoinViewSerializer, GrowthNetworkSerializer, \
    ItemShortSerializer


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
    serializer_class = CommunitiesViewSerializer

    def get_queryset(self):
        return Community.objects.annotate(total_members=Count('members')).order_by("priority")


class CommunitiesJoinView(generics.ListCreateAPIView):
    serializer_class = CommunitiesJoinViewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Community.objects.annotate(
            total_members=Count('members'),
            has_joined=Exists(CommunityMembers.objects.filter(community=OuterRef('pk'), user=self.request.user))
        ).order_by("priority")

    def post(self, request, *args, **kwargs):
        try:
            community = Community.objects.get(community_id=self.request.data.get("community_id", None))
            if self.request.user.team.filter(community=community).exists():
                return Response({"error": "You already have joined {} supply chain".format(community.name)},
                                status=status.HTTP_400_BAD_REQUEST)
            CommunityMembers.objects.create(user=self.request.user, community=community)
            return Response({"msg": "Congratulations you have joined {} Supply chain".format(
                community.name).format(community.name)}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": "invalid community_id passed"}, status=status.HTTP_400_BAD_REQUEST)


class CommunitiesJoinedView(generics.ListAPIView):
    serializer_class = CommunitiesJoinViewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Community.objects.filter(
            id__in=list(self.request.user.team.all().values_list("community__id", flat=True))).annotate(
            total_members=Count('members'),
            has_joined=Exists(CommunityMembers.objects.filter(community=OuterRef('pk'), user=self.request.user))
        ).order_by("priority")


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


class GrowthNetwork(generics.ListAPIView):
    serializer_class = GrowthNetworkSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return Community.objects.get(community_id=self.kwargs['network_id'])
        except Exception as e:
            raise ValidationError("Invalid network_id provided")

    def get_queryset(self):
        try:
            community = self.get_object()
            return community.feed.all().order_by("-added_on")
        except Exception as e:
            return []


class UploadCapabilityPost(generics.CreateAPIView):
    serializer_class = GrowthNetworkSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return Community.objects.get(community_id=self.kwargs['network_id'])
        except Exception as e:
            raise ValidationError("Invalid network_id provided")

    def post(self, request, *args, **kwargs):
        try:
            item = Items.objects.get(id=int(self.request.query_params.get("item_id", 1)))
            community = self.get_object()
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=self.request.user, community=community, item=item, item_name=item.title)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Items.DoesNotExist:
            return Response({"error": "Invalid item_id provided"}, status=status.HTTP_404_NOT_FOUND)