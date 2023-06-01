import csv
import io

from django.shortcuts import render
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response

from skybrain.models import LicensesRequests, Organization, Room
from skybrain.serializers import LicensesViewSerializer, CreateLicensesViewSerializer, OrganizationRoomsSerializer


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


class CreateLicensesView(generics.CreateAPIView):
    serializer_class = CreateLicensesViewSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            csv_file = request.data.get("csv_file", None)
            email = request.data.get("email", None)
            organization = request.data.get("organization", None)
            org, created = Organization.objects.get_or_create(name=organization)
            LicensesRequests.objects.get(organization=organization, email=email, is_approved=True)
            csv_file_text = io.TextIOWrapper(csv_file.file, encoding='utf-8')
            reader = csv.DictReader(csv_file_text)
            for row in reader:
                Room.objects.get_or_create(
                    room_id=row['room_id'], organization=org, defaults={"room_key": row['room_key']})
            return Response(
                dict({"msg": "Congratulations all your rooms has been created"}),
                status=status.HTTP_201_CREATED
            )
        except LicensesRequests.DoesNotExist:
            return Response(
                dict({"msg": "Your request is not approved yet try after sometime"}),
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                dict({"msg": "Some issue at backend please contact admin!!!"}),
                status=status.HTTP_400_BAD_REQUEST
            )


class OrganizationRooms(generics.ListAPIView):
    serializer_class = OrganizationRoomsSerializer

    def get_queryset(self):
        return Room.objects.all()

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

