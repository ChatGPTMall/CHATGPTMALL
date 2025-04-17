import hashlib
import io
import os
import tempfile
import threading
import uuid
import xml.etree.ElementTree as ET
from datetime import timedelta

from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Exists, OuterRef
from django.http import HttpResponse, HttpResponseBadRequest, StreamingHttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
from rest_framework import generics, status, filters
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from engine.models import Community, CommunityMembers, Items, WechatMessages, InternalExceptions, ListingType, \
    WechatOfficialAccount, VoiceCommands, RoomLoginRequests, GeneralRoomLoginRequests, CommunityPosts
from engine.serializers import WeChatListingAPIViewSerializer, WeChatConfigurationAPIViewSerializer, \
    GetItemsViewSerializer
from homelinked.models import HomePlans, HomepageNewFeature, WeChatAccounts, Mp3Files, VendingMachineItem
from homelinked.serializers import HomePlansAPIViewSerializer, HomepageNewFeatureViewSerializer, \
    CommunitiesViewSerializer, GetCreditsHistorySerializer, CommunitiesJoinViewSerializer, GrowthNetworkSerializer, \
    ItemShortSerializer, WeChatAPIViewSerializer, Mp3FileSerializer, VendingMachineAPIViewSerializer
from skybrain.models import Room
from users.admin import ChinaUsersAdmin
from pydub import AudioSegment
import speech_recognition as sr
from gtts import gTTS
from django.core.files import File
from django.core.files.base import ContentFile


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
            try:
                comm_id = self.kwargs['network_id'].split(":")[1]
            except IndexError:
                comm_id = self.kwargs['network_id']
            return Community.objects.get(community_id=comm_id)
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


class WeChatAPIView(generics.ListCreateAPIView, generics.DestroyAPIView):
    serializer_class = WeChatAPIViewSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WechatOfficialAccount.objects.filter(created_by=self.request.user)

    def get_object(self):
        try:
            return WechatOfficialAccount.objects.get(official_id=self.request.query_params.get("official_id", None))
        except Exception as e:
            raise ValidationError({"error": str(e)})

    def perform_create(self, serializer):
        try:
            serializer.save(created_by=self.request.user)
        except Exception as e:
            raise ValidationError({"error": str(e)})

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response({"msg": "Official Account Deleted Successfully"}, status=status.HTTP_200_OK)


class WeChatConfigurationAPIView(generics.CreateAPIView):
    serializer_class = WeChatConfigurationAPIViewSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class WhatsAppLogin(generics.CreateAPIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        otp = request.data.get("otp", None)
        if otp is None:
            return Response({"error": "otp field is required!!!"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Calculate the threshold time (one hour ago from now)
            one_hour_ago = timezone.now() - timedelta(hours=1)
            room_request = GeneralRoomLoginRequests.objects.filter(
                otp=otp, is_expired=False
            ).last()
            if request:
                token, _ = Token.objects.get_or_create(user=room_request.user)

                return Response({
                    "token": str(token),
                    "room_id": str(room_request.user.room.room_id),
                    "room_key": str(room_request.user.room.room_key)
                })
            return Response({"error": "Otp expired/Invalid"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            InternalExceptions.objects.create(text=e)
            return Response({"error": "Otp expired/Invalid"}, status=status.HTTP_400_BAD_REQUEST)


class WechatLogin(generics.CreateAPIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        otp = request.data.get("otp", None)
        if otp is None:
            return Response({"error": "otp field is required!!!"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Calculate the threshold time (one hour ago from now)
            one_hour_ago = timezone.now() - timedelta(hours=1)
            request = RoomLoginRequests.objects.filter(
                otp=otp, is_expired=False
            ).last()
            if request:
                token, _ = Token.objects.get_or_create(user=request.user.user)

                return Response({
                    "token": str(token),
                    "room_id": str(request.user.room.room_id),
                    "room_key": str(request.user.room.room_key)
                })
            return Response({"error": "Otp expired/Invalid"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            InternalExceptions.objects.create(text=e)
            return Response({"error": "Otp expired/Invalid"}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def GetWechatEvents(request):
    if request.method == 'GET':
        # Handle the verification of the server address from Weixin
        signature = request.GET.get('signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')
        token = 'scanpen2024'

        # Create a list of the token, timestamp, and nonce
        data = [token, timestamp, nonce]
        # Sort it
        data.sort()
        # Concatenate into a single string
        temp = ''.join(data)
        # Create a hash object
        hash_obj = hashlib.sha1(temp.encode('utf-8'))
        # Get the hash digest
        hashcode = hash_obj.hexdigest()
        # If it's the same as the signature, return the echostr
        if hashcode == signature:
            return HttpResponse(request.GET.get('echostr', ''), content_type="text/plain")

    if request.method == 'POST':
        # Here, you would handle incoming messages or events
        # and possibly respond to them
        # xml_data = etree.fromstring(request.body)
        request_data = request.body

        # Parse the XML data
        root = ET.fromstring(request_data)

        official_account_id = root.findtext('.//ToUserName')
        pic_url = root.findtext('.//PicUrl')
        wechat_id = root.findtext('.//FromUserName')
        text_content = root.findtext('.//Content')
        msg_type = root.findtext('.//MsgType')
        event_type = root.findtext('.//Event')
        latitude = root.findtext('.//Latitude')
        longitude = root.findtext('.//Longitude')
        precision = root.findtext('.//Precision')
        data = {
            "pic_url": pic_url if pic_url else "",
            "wechat_id": wechat_id if wechat_id else "",
            "official_account_id": official_account_id if official_account_id else "",
            "text": text_content if text_content else "",
            "msg_type": msg_type if msg_type else "",
            "event_type": event_type if event_type else "",
            "latitude": latitude if latitude else "",
            "longitude": longitude if longitude else "",
            "precision": precision if precision else ""
        }
        try:
            if data.get("pic_url"):
                WechatMessages.objects.create(**data)
            if data.get("text"):
                today = timezone.now()
                two_minutes = today.date() - timedelta(minutes=2)
                if not WechatMessages.objects.filter(
                        added_on__gte=two_minutes,
                        text=data.get("text"), wechat_id=data.get("wechat_id"),
                        official_account_id=data.get("official_account_id"),
                        msg_type=data.get("msg_type"), event_type=data.get("event_type")
                ).exists():
                    WechatMessages.objects.create(
                        text=data.get("text"), wechat_id=data.get("wechat_id"),
                        official_account_id=data.get("official_account_id"),
                        msg_type=data.get("msg_type"), event_type=data.get("event_type")
                    )
        except Exception as e:
            InternalExceptions.objects.create(text=e)
        return HttpResponse("Message Received", status=status.HTTP_201_CREATED)

    return HttpResponse("Invalid Request", status=403)


class UploadTencentItems(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        data = self.request.data


class WeChatListingAPIView(generics.ListAPIView):
    serializer_class = WeChatListingAPIViewSerializer
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        return Items.objects.filter(listing=ListingType.WECHAT).order_by("-added_on")


class WhatsappListingAPIView(generics.ListAPIView):
    serializer_class = WeChatListingAPIViewSerializer
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        return Items.objects.filter(listing=ListingType.WHATSAPP).order_by("-added_on")


class WeChatProductDetail(generics.RetrieveAPIView):
    serializer_class = WeChatListingAPIViewSerializer
    authentication_classes = []
    permission_classes = []

    def get_object(self):
        try:
            return Items.objects.get(item_id=self.kwargs.get("item_id"))
        except Items.DoesNotExist:
            raise ValidationError({"error": "Invalid item_id provided"})


class TextToCommandAPIView(generics.RetrieveAPIView):
    authentication_classes = []
    permission_classes = []

    def retrieve(self, request, *args, **kwargs):
        try:
            on_image = None
            off_image = None
            text = self.request.query_params.get("text")
            obj = VoiceCommands.objects.get(input=text)
            command = self.request.query_params.get("command")
            if command.upper() == "ON":
                on_image = obj.on_image.url
            else:
                off_image = obj.off_image.url
            return Response({
                "on_image": on_image,
                "off_image": off_image,
                "switch": obj.switch
            })
        except Exception as e:
            return Response({"error": str(e)})


class RoomItemsV2View(generics.ListAPIView):
    serializer_class = GetItemsViewSerializer
    permission_classes = []
    authentication_classes = []

    def get_object(self):
        try:
            return Room.objects.get(room_key=self.kwargs['room_key'])
        except Exception as e:
            raise ValidationError("Invalid room_key provided")

    def get_queryset(self):
        listing = self.request.query_params.get("listing", "GENERAL")
        return Items.objects.filter(
            item_id__in=list(self.get_object().whatsapp_items.filter(
                listing=listing.upper()).values_list("item__item_id", flat=True))
        )


class CommunityItems(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_communtiy(self, community_id):
        return Community.objects.get(community_id=community_id)

    def post(self, request, *args, **kwargs):
        try:
            item = Items.objects.get(item_id=self.request.data.get("item_id", 1))
            for community_id in self.request.data.get("communities"):
                try:
                    community = self.get_communtiy(community_id)
                    CommunityPosts.objects.create(user=self.request.user, community=community, item=item)
                except Exception as e:
                    pass
            return Response({"msg": "All Items Uploaded"}, status=status.HTTP_201_CREATED)
        except Items.DoesNotExist:
            return Response({"error": "Invalid item_id provided"}, status=status.HTTP_404_NOT_FOUND)


def translate_text(client, recognized_text, language):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": f"convert '{recognized_text}' into {language} language and return only provided text"
            }
        ]
    )

    return  completion.choices[0].message.content



class VoiceToTextView(generics.CreateAPIView):
    """
    POST:
    - file: The MP3 file
    - language: (Optional) a language code for more accurate transcription

    Returns recognized text from the audio using OpenAI Whisper API.
    """

    def post(self, request, *args, **kwargs):
        # 1. Get MP3 file from request
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Get language code (e.g. 'en', 'es')
        language = request.data.get('language', 'en')

        # 3. Create Mp3File entry in DB (this saves the file to S3 or your storage backend)
        mp3_instance = Mp3Files.objects.create(file=file_obj, language=language)

        # 4. Read the file contents into a BytesIO object
        try:
            with mp3_instance.file.open('rb') as f:
                file_bytes = f.read()
            audio_in_memory = io.BytesIO(file_bytes)
        except Exception as e:
            return Response(
                {"error": f"Error reading file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # 5. Prepare the file payload with a known extension & content-type
        #    e.g. "audio.mp3" and "audio/mpeg"
        #    This ensures the OpenAI library can detect the file type properly.
        file_payload = (
            "audio.mp3",         # pretend filename
            audio_in_memory,     # file-like object
            "audio/mpeg"         # content type
        )

        # 6. Instantiate your OpenAI client
        client = OpenAI()

        # 7. Transcribe using client.audio.transcriptions.create()
        try:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=file_payload,
                # Optional: specify language for better accuracy if known
                prompt=f"convert it into {language}"
            )
        except Exception as e:
            return Response(
                {"error": f"OpenAI transcription error: {str(e)}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        # 8. Extract recognized text from the transcription response
        recognized_text = transcription.text

        translated = translate_text(client, recognized_text, language)

        # 9. Store recognized_text in the Mp3Files entry (if desired)
        mp3_instance.recognized_text = translated
        mp3_instance.save()

        # 10. Return the recognized text
        return Response({"id": mp3_instance.id, "recognized_text": translated})

class TextToVoiceView(generics.CreateAPIView):
    """
    POST:
    - text: Text to convert to speech
    - language: Language code (e.g. 'en', 'es')

    Returns a JSON with the Mp3File record, which contains the URL to the generated MP3.
    """

    def post(self, request, *args, **kwargs):
        text = request.data.get('text')
        language = request.data.get('language', 'en')

        # Initialize OpenAI client (adjust import/path as needed)
        client = OpenAI()

        text = translate_text(client, text, language)

        if not text:
            return Response({"error": "No text provided."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Create a unique file name for the MP3
        file_name = f"{uuid.uuid4()}.mp3"
        speech_file_path = os.path.join(settings.MEDIA_ROOT, file_name)

        instructions = (
            f"Speak clearly in {language}  language only. "
            "Maintain a natural flow appropriate to the language."
        )

        # Use OpenAI TTS to stream audio to file
        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=text,
            instructions=instructions,
        ) as response:
            response.stream_to_file(speech_file_path)

        # Create Mp3Files instance
        with open(speech_file_path, 'rb') as f:
            django_file = File(f)
            django_file.name = file_name  # e.g. "ec152b63-83a2-...mp3"

            mp3_instance = Mp3Files.objects.create(
                file=django_file,
                language=language
            )

        # (Optional) delete the file from disk if you wish to keep only DB storage
        if os.path.exists(speech_file_path):
            os.remove(speech_file_path)

        serializer = Mp3FileSerializer(mp3_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class VendingMachineAPIView(generics.ListAPIView):
    serializer_class = VendingMachineAPIViewSerializer

    def get_queryset(self):
        return VendingMachineItem.objects.all()


def text_generate(prompt: str) -> str:
    # switch to the “mini” chat model (much faster)
    client = OpenAI()
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content


class VoiceToVoiceView(generics.CreateAPIView):
    serializer_class = []
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        text = request.data.get('text')
        response = text_generate(text)

        return Response({
            "response": response
        }, status=status.HTTP_200_OK)


class VoiceAPIView(generics.CreateAPIView):
    """
    POST:
    - text: Text to convert to speech
    - language: Language code (e.g. 'en', 'es')

    Returns a JSON with the Mp3File record, which contains the URL to the generated MP3.
    """

    def post(self, request, *args, **kwargs):
        text = request.data.get('text')
        language = request.data.get('language', 'en')

        # Initialize OpenAI client (adjust import/path as needed)
        client = OpenAI()

        text = text_generate(text)

        if not text:
            return Response({"error": "No text provided."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Create a unique file name for the MP3
        file_name = f"{uuid.uuid4()}.mp3"
        speech_file_path = os.path.join(settings.MEDIA_ROOT, file_name)

        # Use OpenAI TTS to stream audio to file
        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=text,
        ) as response:
            response.stream_to_file(speech_file_path)

        # Create Mp3Files instance
        with open(speech_file_path, 'rb') as f:
            django_file = File(f)
            django_file.name = file_name  # e.g. "ec152b63-83a2-...mp3"

            mp3_instance = Mp3Files.objects.create(
                file=django_file,
                language=language
            )

        # (Optional) delete the file from disk if you wish to keep only DB storage
        if os.path.exists(speech_file_path):
            os.remove(speech_file_path)

        serializer = Mp3FileSerializer(mp3_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

