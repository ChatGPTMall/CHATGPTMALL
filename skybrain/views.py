from django.shortcuts import render
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response

from skybrain.models import LicensesRequests
from skybrain.serializers import LicensesViewSerializer


class LicensesView(generics.CreateAPIView):
    serializer_class = LicensesViewSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        today = timezone.now()
        if LicensesRequests.objects.filter(
                organization=request.data.get("organization"), added_on__date=today.date()).exists():
            return Response(
                dict({"msg": "You already have requested for licenses please wait till we approve your previous request"}),
                status=status.HTTP_200_OK
            )
        serializer.save()
        return Response(
            dict({"msg": "Your request has been successfully submitted we will shortly get in touch with you"}),
            status=status.HTTP_201_CREATED
        )