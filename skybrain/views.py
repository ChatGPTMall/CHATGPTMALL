# import csv
# import io
#
# from django.conf import settings
# from django.core.mail import send_mail
# from django.shortcuts import render
# from django.utils import timezone
# from rest_framework import generics, status, filters
# from rest_framework.exceptions import ValidationError
# from rest_framework.pagination import PageNumberPagination
# from rest_framework.response import Response
# from django_filters.rest_framework import DjangoFilterBackend
# # from skybrain.models import LicensesRequests, Organization, Room, RoomItems, CustomerSupport
# # from skybrain.serializers import LicensesViewSerializer, CreateLicensesViewSerializer, OrganizationRoomsSerializer, \
# #     SkybrainCustomerRoomSerializer, HistoryRoomSerializer, ItemsRoomViewSerializer, OrganizationsviewSerializer, \
# #     CSQueriesViewSerializer
#
#
# class LicensesView(generics.CreateAPIView):
#     serializer_class = LicensesViewSerializer
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         today = timezone.now()
#         org = request.data.get("organization")
#         email = request.data.get("email")
#         no_of_licenses = request.data.get("no_of_licenses")
#         if LicensesRequests.objects.filter(
#                 organization=request.data.get("organization"), added_on__date=today.date()).exists():
#             return Response(
#                 dict({"msg": "You already have requested for licenses please wait till we approve your previous request"}),
#                 status=status.HTTP_200_OK
#             )
#         serializer.save()
#         plain_message = "Hi \n\n " \
#                         "New Account Request from {} for {}\n" \
#                         "No of Licenses Required: {} \n\n" \
#                         "Thanks & Regards \n" \
#                         "Backend Team".format(email, org, no_of_licenses)
#         recipient_list = ["faisalbashir353@gmail.com", "bennyliao@thingsbook.me"]
#         send_mail(
#             "New Accounts Request from {}".format(org), plain_message, settings.EMAIL_HOST_USER,
#             recipient_list, fail_silently=True)
#         plain_txt = "Hi \n\n" \
#                     "Thanks for sending request to skybrain our sales team will be in touch with you shortly \n\n" \
#                     "Regards \n" \
#                     "SkyBrain"
#         send_mail(
#             "Accounts Request Submitted", plain_txt, settings.EMAIL_HOST_USER, [email], fail_silently=True
#         )
#         return Response(
#             dict({"msg": "Your request has been successfully submitted we will shortly get in touch with you"}),
#             status=status.HTTP_201_CREATED
#         )
#
#
# class CreateLicensesView(generics.CreateAPIView):
#     serializer_class = CreateLicensesViewSerializer
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         try:
#             csv_file = request.data.get("csv_file", None)
#             email = request.data.get("email", None)
#             organization = request.data.get("organization", None)
#             org, created = Organization.objects.get_or_create(name=organization)
#             LicensesRequests.objects.get(organization=organization, email=email, is_approved=True)
#             csv_file_text = io.TextIOWrapper(csv_file.file, encoding='utf-8')
#             reader = csv.DictReader(csv_file_text)
#             for row in reader:
#                 Room.objects.get_or_create(
#                     room_id=row['room_id'], organization=org, defaults={"room_key": row['room_key']})
#             return Response(
#                 dict({"msg": "Congratulations all your rooms has been created"}),
#                 status=status.HTTP_201_CREATED
#             )
#         except LicensesRequests.DoesNotExist:
#             return Response(
#                 dict({"msg": "Your request is not approved yet try after sometime"}),
#                 status=status.HTTP_200_OK
#             )
#         except Exception as e:
#             return Response(
#                 dict({"msg": "Some issue at backend please contact admin!!!"}),
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#
# class OrganizationRooms(generics.ListAPIView):
#     serializer_class = OrganizationRoomsSerializer
#
#     def get_queryset(self):
#         return Room.objects.all()
#
#     def list(self, request, *args, **kwargs):
#         serializer = self.get_serializer(self.get_queryset(), many=True)
#         return Response(serializer.data)
#
#
# class SkybrainCustomerRoom(generics.CreateAPIView):
#     serializer_class = SkybrainCustomerRoomSerializer
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         try:
#             Room.objects.get(
#                 organization__name=request.data.get("organization"), room_id=int(request.data.get("room_id")),
#                 room_key=request.data.get("room_key"))
#             return Response(
#                 dict({"msg": "Entered Room Successfully"}),
#                 status=status.HTTP_201_CREATED
#             )
#         except Exception as e:
#             return Response(dict({"error": "Invalid Room Key Found"}), status=status.HTTP_400_BAD_REQUEST)
#
#
# class ValidateRoom(generics.ListAPIView):
#
#     def get(self, request, *args, **kwargs):
#         room_id = request.query_params.get("room_id", None)
#         room_key = request.query_params.get("room_key", None)
#         if Room.objects.filter(room_id=int(room_id), room_key=room_key).exists():
#             return Response({"msg": "request validated successfully"}, status=status.HTTP_200_OK)
#         return Response({"error": "Invalid Credentials Provided"}, status=status.HTTP_400_BAD_REQUEST)
#
#
# class StandardResultsSetPagination(PageNumberPagination):
#     page_size = 30
#     page_size_query_param = 'page_size'
#     max_page_size = 100
#
#
# class HistoryRoom(generics.ListAPIView):
#     serializer_class = HistoryRoomSerializer
#     pagination_class = StandardResultsSetPagination
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     search_fields = ['added_on', ]
#
#     def get_queryset(self):
#         try:
#             room_id = self.request.query_params.get("room_id", None)
#             room_key = self.request.query_params.get("room_key", None)
#             room = Room.objects.get(room_id=int(room_id), room_key=room_key)
#             return room.history.all()
#         except Exception as e:
#             raise ValidationError(dict({"error": "invalid room_id provided"}))
#
#     def list(self, request, *args, **kwargs):
#         query_set = self.filter_queryset(self.get_queryset())
#         page = self.paginate_queryset(query_set)
#         serializer = self.get_serializer(page, many=True)
#         if page is not None:
#             return self.get_paginated_response(serializer.data)
#         return Response(serializer.data)
#
#     def get(self, request, *args, **kwargs):
#         return self.list(self, request, *args, **kwargs)
#
#
# class ItemsRoomView(generics.ListAPIView):
#     serializer_class = ItemsRoomViewSerializer
#     pagination_class = StandardResultsSetPagination
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     search_fields = ['name', 'description', 'added_on', 'category', 'is_private']
#
#     def get_queryset(self):
#         try:
#             room_id = self.request.query_params.get("room_id", None)
#             is_private = self.request.query_params.get("is_private", None)
#             if is_private:
#                 if int(is_private) == 1:
#                     return RoomItems.objects.filter(room__room_id=int(room_id), is_private=True)
#                 if int(is_private) == 0:
#                     return RoomItems.objects.filter(room__room_id=int(room_id), is_private=False)
#             return RoomItems.objects.filter(room__room_id=int(room_id))
#         except Exception as e:
#             raise ValidationError(dict({"error": "invalid room_id provided"}))
#
#     def list(self, request, *args, **kwargs):
#         query_set = self.filter_queryset(self.get_queryset())
#         page = self.paginate_queryset(query_set)
#         serializer = self.get_serializer(page, many=True)
#         if page is not None:
#             return self.get_paginated_response(serializer.data)
#         return Response(serializer.data)
#
#     def get(self, request, *args, **kwargs):
#         return self.list(self, request, *args, **kwargs)
#
#
# class PublicItemsRoomView(generics.ListAPIView):
#     serializer_class = ItemsRoomViewSerializer
#     pagination_class = StandardResultsSetPagination
#
#     def get_queryset(self):
#         try:
#             room_id = self.request.query_params.get("room_id", None)
#             return RoomItems.objects.filter(room__room_id=int(room_id), is_private=False)
#         except Exception as e:
#             raise ValidationError(dict({"error": "invalid room_id provided"}))
#
#     def list(self, request, *args, **kwargs):
#         query_set = self.filter_queryset(self.get_queryset())
#         page = self.paginate_queryset(query_set)
#         serializer = self.get_serializer(page, many=True)
#         if page is not None:
#             return self.get_paginated_response(serializer.data)
#         return Response(serializer.data)
#
#     def get(self, request, *args, **kwargs):
#         return self.list(self, request, *args, **kwargs)
#
#
# class UploadItemsRoomView(generics.CreateAPIView):
#     serializer_class = ItemsRoomViewSerializer
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         # room = Room.objects.get(room_id=int(request.data.get("room_id")))
#         # print(room)
#         serializer.save()
#         return Response(serializer.data)
#
#
# class Organizationsview(generics.ListAPIView):
#     serializer_class = OrganizationsviewSerializer
#     pagination_class = StandardResultsSetPagination
#     permission_classes = []
#     authentication_classes = []
#
#     def get_queryset(self):
#         return Organization.objects.all()
#
#     def list(self, request, *args, **kwargs):
#         query_set = self.filter_queryset(self.get_queryset())
#         page = self.paginate_queryset(query_set)
#         serializer = self.get_serializer(page, many=True)
#         if page is not None:
#             return self.get_paginated_response(serializer.data)
#         return Response(serializer.data)
#
#
# class CSQueriesView(generics.ListAPIView):
#     serializer_class = CSQueriesViewSerializer
#     pagination_class = StandardResultsSetPagination
#     permission_classes = []
#     authentication_classes = []
#
#     def get_queryset(self):
#         try:
#             room_key = self.request.query_params.get("room_key", None)
#             room = Room.objects.get(room_key=room_key)
#             return room.room_support.all()
#         except Exception as e:
#             raise ValidationError(dict({"error": "invalid room_key provided"}))
#
#     def list(self, request, *args, **kwargs):
#         query_set = self.filter_queryset(self.get_queryset())
#         page = self.paginate_queryset(query_set)
#         serializer = self.get_serializer(page, many=True)
#         if page is not None:
#             return self.get_paginated_response(serializer.data)
#         return Response(serializer.data)