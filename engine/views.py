import base64
import json
import os
import ast
import random
import re
import string
import tempfile
import time
import urllib
from json import JSONDecodeError
from pathlib import Path

import openai
import stripe
import requests
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema

from django.core.files.base import ContentFile
from drf_spectacular.utils import extend_schema
from openai import OpenAI
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError

from engine.assistants import create_assistant
from engine.authentication import HMACAuthentication
from engine.permissions import HaveCredits
from engine.thread_functions import run_in_thread
from homelinked.models import CreditsHistory, FeaturesChoices
from homelinked.serializers import RedeemCouponViewSerializer, ItemPurchasesSerializer
from skybrain.models import Room, CustomerSupport
from users.models import RoomHistory
from users.models import User
from django.urls import reverse
from django.conf import settings
from django.core.files import File
from urllib.request import urlopen
from rest_framework import generics, status
from PIL import Image, ImageDraw, ImageFont
from rest_framework.response import Response
from django.shortcuts import render, redirect
from engine.models import ImagesDB, ImageAnalysisDB, Items, Category, KeyManagement, Community, CommunityPosts, \
    BankAccounts, CouponCode, FeedLikes, Purchases, Chatbots, WhatsappConfiguration, PrivateBankAccounts, \
    WhatsappAccountRequest, ChatBotHistory, ListingType, GeneralRoomLoginRequests
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from engine.serializers import TextToTexTViewSerializer, ImageAnalysisViewSerializer, ShopItemsViewSerializer, \
    ShopCategoriesViewSerializer, GetItemsViewSerializer, TextToTexTMicrosoftViewSerializer, TranscribeAudioSerializer, \
    TextToTexTViewImageSerializer, VisionViewSerializer, PostLikeViewSerializer, PostCommentViewSerializer, \
    GetPostsViewSerializer, NetworkPostItemSessionCheckoutSerializer, ChatbotAPIViewSerializer, \
    WhatsappConfigurationSerializer, ItemsBulkCreateSerializer

from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from PIL import Image
from engine.models import Items

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET


class TextToTexTView(generics.CreateAPIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = VisionViewSerializer
    permission_classes = [IsAuthenticated, HaveCredits]

    # Function to encode the image
    def encode_image(self, image_path):
        # with open(image_path, "rb") as image_file:
        file_content = image_path.read()
        return base64.b64encode(file_content).decode('utf-8')

    @swagger_auto_schema(
        tags=["Homelinked APIs"]
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        openai_key = KeyManagement.objects.filter(platform="OPENAI").last()
        input_ = request.data["input"]
        input_image = request.data["image"]
        encode_image = self.encode_image(input_image)
        if openai_key:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {openai_key.key}"
            }

            payload = {
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": input_
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{encode_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 300
            }

            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            user = self.request.user
            user.credits -= 1
            user.save()
            CreditsHistory.create_credits(user, 1, FeaturesChoices.VISION)
            return Response(dict({
                "input": input_,
                "response": response.json()["choices"][0]["message"]["content"]
            }), status=status.HTTP_201_CREATED)
        return Response({"error": "Some issues at backend please contact admin"},
                        status=status.HTTP_200_OK)


class RoomTextToTexTView(generics.CreateAPIView):
    
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = TextToTexTViewImageSerializer
    permission_classes = [IsAuthenticated]

    # Function to encode the image
    def encode_image(self, image_path):
        # with open(image_path, "rb") as image_file:
        file_content = image_path.read()
        return base64.b64encode(file_content).decode('utf-8')

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        room_id = request.query_params.get("room_key", None)
        language = request.query_params.get("language", None)
        translate = request.query_params.get("translate", None)
        input_ = request.data["input"]
        try:
            try:
                support = request.data["customer_support"]
            except KeyError:
                support = 0
            if language:
                input_lang = input_ + " " + "in" + language
            elif translate:
                input_lang = "convert" + " " + '"{}"'.format(input_) + " " + "into" + " " + translate
            else:
                input_lang = input_
            history = None
            his_image = None
            openai_key = KeyManagement.objects.filter(platform="OPENAI").last()
            room_history = RoomHistory.objects.filter(user_input=input_)
            result = ""
            if "file" in request.data.keys():
                input_image = request.data["file"]
                encode_image = self.encode_image(input_image)
                if openai_key:
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {openai_key.key}"
                    }

                    payload = {
                        "model": "gpt-4-vision-preview",
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "{}".format(input_)
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{encode_image}"
                                        }
                                    }
                                ]
                            }
                        ],
                        "max_tokens": 300
                    }

                    response = requests.post(
                        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
                    )
                    try:
                        result = response.json()["choices"][0]["message"]["content"]
                    except JSONDecodeError as e:
                        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                    except Exception as e:
                        return Response(response.json())
            else:
                input_image = None
                if openai_key:
                    if not room_history.exists():
                        client = OpenAI()
                        response = client.completions.create(
                            model="gpt-3.5-turbo-instruct",
                            prompt=input_,
                            max_tokens=int(3000),
                            stop=None,
                        )
                        for object in response:
                            if "choices" in object:
                                response2 = object[1][0]
                                for object2 in response2:
                                    if "text" in object2:
                                        result = object2[1]
                    else:
                        result = room_history.last().response
            if room_id:
                try:
                    room = Room.objects.get(room_key=room_id)
                    if translate:
                        history, his_image = self.create_history(room, input_lang, result, input_image)
                    else:
                        history, his_image = self.create_history(room, input_, result, input_image)
                    if int(support) == 1:
                        CustomerSupport.objects.create(user_input=input_, response=result, room=room)
                except Room.DoesNotExist:
                    return Response({"error": "Invalid room_id provided"}, status=status.HTTP_400_BAD_REQUEST)
            CreditsHistory.create_credits(self.request.user, 1, FeaturesChoices.GENERAL)
            return Response(dict({
                "input": input_,
                "image": his_image.url if his_image else None ,
                "response": result,
                "history": history
            }), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(e)

    def create_history(self, room, input_, response, image=None):
        if image:
            history = RoomHistory.objects.create(
                room=room, user_input=input_, response=response, user=self.request.user,
                image=image
            )
        else:
            history = RoomHistory.objects.create(
                room=room, user_input=input_, response=response, user=self.request.user
            )
        return history.id, history.image


class TextToTexTOpeniaiView(generics.CreateAPIView):
    serializer_class = TextToTexTViewSerializer
    permission_classes = [IsAuthenticated, HaveCredits]

    @swagger_auto_schema(
        tags=["Homelinked APIs"]
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            input_ = request.data["input"]
            client = OpenAI()
            response = client.completions.create(
                model="gpt-3.5-turbo-instruct",
                prompt=input_,
                max_tokens=int(3000),
                stop=None,
            )
            for object in response:
                if "choices" in object:
                    response2 = object[1][0]
                    for object2 in response2:
                        if "text" in object2:
                            result = object2[1]
            user = self.request.user
            user.credits -= 1
            user.save()
            CreditsHistory.create_credits(user, 1, FeaturesChoices.TEXT_TO_TEXT)
            return Response(dict({
                "input": input_,
                "response": result
            }), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TextToTexTMicrosoftView(generics.CreateAPIView):
    
    serializer_class = TextToTexTMicrosoftViewSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            openai.api_key = self.request.data.get("ms_key")
            endpoint = self.request.data.get("endpoint")
            input_ = self.request.data.get("input")
            openai.api_base = "{}".format(endpoint)
            openai.api_type = 'azure'
            openai.api_version = "2023-03-15-preview"
            model = "davinci"
            response = openai.Completion.create(
                engine=model,
                max_tokens=int(3000),
                prompt=input_,)
            text = response['choices'][0]['text'].replace('\n', '').replace(' .', '.').strip()
            return Response(dict({
                "input": input_,
                "response": text
            }), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TranscribeAudio(generics.CreateAPIView):
    
    serializer_class = TranscribeAudioSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        openai.api_key = os.getenv("OPEN_AI_KEY")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            print(self.request.data)
            audio = self.request.data.get("audio").temporary_file_path()
            audio_file = open(audio, "rb")
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
            return Response(dict({"response": transcript["text"]}))
        except Exception as e:
            return Response(dict({"error": str(e)}))


class TextToImageView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, HaveCredits]
    serializer_class = TextToTexTViewSerializer

    @swagger_auto_schema(
        tags=["Homelinked APIs"]
    )
    def post(self, request, *args, **kwargs):
        URL = os.getenv("DEPLOYED_HOST", "https://chatgptmall.tech")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        input_ = request.data["input"]
        internal_image = ImagesDB.objects.filter(question=input_)
        if not internal_image:
            client = OpenAI()
            response = client.images.generate(
                model="dall-e-3", prompt=input_, size="1024x1024", quality="standard", n=1,
            )
            image_url = response.data[0].url
            image = ImagesDB.objects.create(question=input_, user=self.request.user)
            response = urlopen(image_url)
            io = BytesIO(response.read())
            image.image.save("{}.jpg".format(input_), File(io))
        else:
            image = internal_image.last()
        user = self.request.user
        user.credits -= 1
        user.save()
        CreditsHistory.create_credits(user, 1, FeaturesChoices.TEXT_TO_IMAGE)
        return Response(dict({
            "input": input_,
            "image": image.image.url if image.image else None
        }), status=201)


class GetTaobaoItems(generics.ListAPIView):
    permission_classes = [IsAuthenticated, HaveCredits]

    @swagger_auto_schema(
        tags=["Homelinked APIs"]
    )
    def get(self, request, *args, **kwargs):
        search = self.request.query_params.get("search")
        page = self.request.query_params.get("page_no", 1)

        url = "https://taobao-api.p.rapidapi.com/api"

        querystring = {"q": "{}".format(search), "api": "item_search", "page": int(page)}

        headers = {
            "X-RapidAPI-Key": settings.TAOBAO_KEY,
            "X-RapidAPI-Host": "taobao-api.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)
        user = self.request.user
        user.credits -= 1
        user.save()
        CreditsHistory.create_credits(user, 1, FeaturesChoices.TAOBAO)
        return Response(response.json())


class GetCurrencies(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get_currencies(self):

        url = "https://currency-converter-pro1.p.rapidapi.com/currencies"

        headers = {
            "X-RapidAPI-Key": settings.TAOBAO_KEY,
            "X-RapidAPI-Host": "currency-converter-pro1.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers)
        return list(response.json()["result"].keys())

    @swagger_auto_schema(
        tags=["Homelinked APIs"]
    )
    def get(self, request, *args, **kwargs):
        currencies_list = self.get_currencies()
        currencies_list.remove('VEF')
        currencies = ",".join(currencies_list)
        url = "https://currency-converter-pro1.p.rapidapi.com/latest-rates"

        querystring = {"base": "USD", "currencies": str(currencies)}

        headers = {
            "X-RapidAPI-Key": settings.TAOBAO_KEY,
            "X-RapidAPI-Host": "currency-converter-pro1.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)

        return Response(response.json())


class ImageAnalysisView(generics.CreateAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = ImageAnalysisViewSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image_url = request.data["image_url"]
        url = "https://microsoft-computer-vision3.p.rapidapi.com/describe?language=en&maxCandidates=1&descriptionExclude%5B0%5D=Celebrities"

        querystring = {"language": "en", "maxCandidates": "1", "descriptionExclude[0]": "Celebrities"}

        payload = {"url": image_url}
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": "3ec1eef879msh365ea5d96552e49p15a7e9jsn95f1d7c21fd9",
            "X-RapidAPI-Host": "microsoft-computer-vision3.p.rapidapi.com"
        }

        response = requests.request("POST", url, json=payload, headers=headers, params=querystring)
        return Response(response.json(), status=status.HTTP_201_CREATED)


class ObjectsDetectionView(generics.CreateAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = ImageAnalysisViewSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image_url = request.data["image_url"]
        result = urllib.request.urlretrieve(image_url)
        image = Image.open(File(open(result[0], "rb")))
        URL = os.getenv("DEPLOYED_HOST", "https://madeinthai.org")
        url = "https://microsoft-computer-vision3.p.rapidapi.com/detect"

        payload = {
            "url": str(image_url)
        }
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": "3ec1eef879msh365ea5d96552e49p15a7e9jsn95f1d7c21fd9",
            "X-RapidAPI-Host": "microsoft-computer-vision3.p.rapidapi.com"
        }

        response = requests.request("POST", url, json=payload, headers=headers)
        results = response.json()
        image_draw = ImageDraw.Draw(image)
        # font = ImageFont.truetype('arial.ttf', 16)
        for obj in results["objects"]:
            left = obj["rectangle"]["x"]
            top = obj["rectangle"]["y"]
            width = obj["rectangle"]["w"]
            height = obj["rectangle"]["h"]
            shape = [(left, top), (left + width, top + height)]
            image_draw.rectangle(shape, outline='blue', width=3)
            text = f'{obj["object"]} ({obj["confidence"] * 100}%)'
            image_draw.text((left + 5 - 1, top + height - 30 + 1), text, (0, 0, 0))
            image_draw.text((left + 5, top + height - 30), text, (255, 0, 0))
        blob = BytesIO()
        image.save(blob, 'JPEG')
        final_image = ImageAnalysisDB.objects.create(file=File(blob))
        final_image.file.save("test.png", File(blob))
        data = dict({
            "url": URL + str(final_image.file.url),
            "results": results
        })
        return Response(data)


class ShopItemsView(generics.CreateAPIView):
    
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ShopItemsViewSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category, created = Category.objects.get_or_create(title=request.data["category"])
        if not Items.objects.filter(title=request.data["title"]).exists():
            item = Items.objects.create(
                title=request.data["title"], description=request.data.get("description", None),
                image=request.data['image'], category=category, price=float(request.data["price"]))
            for community in json.loads(request.data["communities"]):
                try:
                    com = Community.objects.get(name=community)

                    post = CommunityPosts.objects.create(
                        question=request.data["title"], response=request.data.get("description", None),
                        community=com
                    )
                    result = urllib.request.urlretrieve(item.qr_code.url)
                    with open(result[0], 'rb') as f:
                        # Set the image field to the downloaded file
                        post.qrcode.save("test.png", File(f))
                    post.item = item
                    post.save()
                except Exception as e:
                    pass
            URL = os.getenv("DEPLOYED_HOST", "https://chatgptmall.tech")
            return Response({
                "item_id": item.id,
                "category_id": category.id,
                "category_title": category.title,
                "title": item.title,
                "description": item.description,
                "image": item.image.url,
                "added_on": item.added_on,
                "updated_on": item.updated_on
            }, status=status.HTTP_201_CREATED)
        return Response({"error": "item already exists"}, status=status.HTTP_400_BAD_REQUEST)


class GetItemsView(generics.ListCreateAPIView):
    
    serializer_class = GetItemsViewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Items.objects.all()

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            community_id = self.request.query_params.get("community_id")
            community = Community.objects.get(community_id=community_id)
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            is_bank = data.get("public_bank", None)
            if not is_bank:
                stripe_private_key = data.get("stripe_private_key")
                stripe_public_key = data.get("stripe_public_key")
                stripe_webhook_key = data.get("stripe_webhook_key", "None")
                instance, created = PrivateBankAccounts.objects.get_or_create(
                    user=self.request.user, private_key=stripe_private_key,
                    public_key=stripe_public_key, webhook_key=stripe_webhook_key
                )
                serializer.save(
                    vendor=self.request.user, vendor_email=self.request.user.email, private_bank=instance
                )
            else:
                serializer.save(vendor=self.request.user, vendor_email=self.request.user.email)
            item_instance = Items.objects.get(id=serializer.data.get("id"))
            CommunityPosts.objects.create(community=community, user=self.request.user, item=item_instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ShopCategoriesView(generics.ListAPIView):
    
    serializer_class = ShopCategoriesViewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.all()


# for payments
def CreateCheckoutSessionView(request):
    try:
        if request.user.is_authenticated:
            user = User.objects.get(email=request.POST.get("user"))
            plan_name = request.POST.get("plan_name")
            plan_id = request.POST.get("plan_id")
            total_price = float(request.POST.get("total_price"))
            if total_price > 0:
                host = request.get_host()
                checkout_session = stripe.checkout.Session.create(
                    line_items=[
                        {
                            'price_data': {
                                'currency': 'usd',
                                'unit_amount': int(total_price*100),
                                'product_data': {
                                    'name': plan_name,
                                }
                            },
                            'quantity': 1,
                        },
                    ],
                    mode='payment',
                    metadata=dict({"data": str("test")}),
                    customer_email=user,
                    success_url="http://{}{}".format(host, reverse(
                        'payment-success', kwargs={"plan_id": plan_id, "user_id": user.id})),
                    cancel_url="http://{}{}".format(host, reverse('payment-cancel')),
                )
            else:
                return redirect("/payment/success/{}/{}/".format(plan_id, user.id))
        else:
            return redirect("/api/login/")
    except Exception as e:
        return render(request, "404.html", {"e": e})

    return redirect(checkout_session.url, code=303)


def ItemCreateCheckoutSessionView(request):

    try:
        if request.user.is_authenticated:
            item_id = request.POST.get("item_id")
            purchase_id = request.POST.get("purchase_id")
            item = Items.objects.get(pk=int(item_id))
            if item.public_bank:
                SECRET_KEY = item.public_bank.private_key
                WEBHOOK_SECRET = item.public_bank.webhook_key
            if item.private_bank:
                SECRET_KEY = item.private_bank.private_key
                WEBHOOK_SECRET = item.private_bank.webhook_key
            stripe.api_key = SECRET_KEY
            stripe.endpoint_secret = WEBHOOK_SECRET
            user = User.objects.get(email=request.POST.get("user"))
            item_name = request.POST.get("item_name")
            total_price = float(request.POST.get("total_price"))
            if total_price > 0:
                host = request.get_host()
                checkout_session = stripe.checkout.Session.create(
                    line_items=[
                        {
                            'price_data': {
                                'currency': 'usd',
                                'unit_amount': int(total_price*100),
                                'product_data': {
                                    'name': item_name,
                                }
                            },
                            'quantity': 1,
                        },
                    ],
                    mode='payment',
                    metadata=dict({"data": str("test")}),
                    customer_email=user,
                    success_url="http://{}{}".format(host, reverse(
                        'item-payment-success', kwargs={"item_id": item.item_id, "user_id": user.user_id,
                                                        "purchase_id": purchase_id})),
                    cancel_url="http://{}{}".format(host, reverse('payment-cancel')),
                )
            else:
                return redirect("/item/payment/success/{}/{}/{}/".format(item.item_id, user.user_id, purchase_id))
        else:
            return redirect("/api/login/")
    except Exception as e:
        return render(request, "404.html", {"e": e})

    return redirect(checkout_session.url, code=303)


class GrowthNetworkFilters(generics.ListAPIView):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.all().values("title", "id")
        banks = BankAccounts.objects.all().values("name", "id")
        return Response({
            "categories": categories,
            "banks": banks
        })


class RedeemCouponView(generics.CreateAPIView):
    serializer_class = RedeemCouponViewSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            coupon_code = self.request.data.get("coupon_code")
            coupon = CouponCode.objects.get(code=coupon_code)
            if not coupon.is_expired:
                coupon.is_expired = True
                coupon.save()
                return Response({
                    "msg": "Coupon Redeemed Successfully",
                    "discount": coupon.price
                }, status=status.HTTP_201_CREATED
                )
            return Response({"error": "Expired Coupon Provided"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Invalid coupon_code provided"}, status=status.HTTP_404_NOT_FOUND)


class ItemPurchases(generics.ListCreateAPIView, generics.UpdateAPIView):
    serializer_class = ItemPurchasesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.user_purchases.all()

    def get_object(self):
        try:
            return Purchases.objects.get(purchase_id=self.request.query_params.get("purchase_id", None))
        except Exception as e:
            return None

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            if not instance.is_modified:
                is_paid = int(self.request.query_params.get("is_paid"))
                is_purchased = int(self.request.query_params.get("is_purchased"))
                is_paid = True if is_paid == 1 else False
                is_purchased = True if is_purchased == 1 else False
                instance.is_modified = True
                instance.is_paid = is_paid
                instance.is_purchased = is_purchased
                instance.save()
                return Response({"msg": "Purchase Updated Successfully"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Session Expired Try another item id"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Invalid purchase_id found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user=self.request.user, buyer_email=self.request.user.email,
            purchase_date=timezone.now())
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PostLikeView(generics.CreateAPIView):
    """
        API to like a feed editorial & return total no of likes on feed
        if post is already liked then it returns error message
    """
    serializer_class = PostLikeViewSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        try:
            post = CommunityPosts.objects.get(post_id=self.request.data.get("post_id"))
            like = self.request.data.get("like")
            if int(like) == 1:
                if post.post_likes.filter(user=self.request.user).exists():
                    return Response(
                        dict({
                            "msg": "You already have liked this post"
                        }),
                        status=status.HTTP_400_BAD_REQUEST
                    )
                FeedLikes.objects.create(user=self.request.user, post=post)
            else:
                post.post_likes.filter(user=self.request.user).delete()
            return Response(
                dict({
                    "like_count": post.post_likes.all().count(),
                    "liked": True if post.post_likes.filter(user=self.request.user).exists() else False
                }),
                status=status.HTTP_201_CREATED
            )
        except CommunityPosts.DoesNotExist:
            return Response(dict({
                "error": "invalid post_id found"
            },
                status=status.HTTP_400_BAD_REQUEST
            ))


class PostCommentView(generics.ListCreateAPIView):
    """
    API to save & return users comment in FeedComments models
    returns 404 if invalid or no data is passed
    """
    serializer_class = PostCommentViewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            post_id = self.request.query_params.get("post_id", None)
            feed = CommunityPosts.objects.get(post_id=post_id)
            return feed.comments.all().order_by("-added_on")
        except Exception as e:
            print(e)
            raise ValidationError(dict({"error": "Invalid post_id found"}))

    def create(self, request, *args, **kwargs):
        data = self.request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        post_id = data.get("post", None)
        post = CommunityPosts.objects.get(post_id=post_id)
        serializer.save(user=self.request.user, post=post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def post(self, request, *args, **kwargs):
        return self.create(self, request, *args, **kwargs)


class GetPostsView(generics.ListAPIView):
    serializer_class = GetPostsViewSerializer

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


class PostDetailView(generics.ListAPIView):
    def get_object(self):
        try:
            post_id = self.request.query_params.get("post_id", None)
            return CommunityPosts.objects.get(post_id=post_id)
        except Exception as e:
            raise ValidationError(dict({"error": "Invalid post_id found"}))

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = GetPostsViewSerializer(instance)
        return Response(serializer.data)


class ItemsBulkCreate(generics.CreateAPIView):
    serializer_class = GetItemsViewSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = self.request.data
        communities = self.request.data.get("communities")
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(vendor=self.request.user, vendor_email=self.request.user.email)
        item_instance = Items.objects.get(id=serializer.data.get("id"))

        if isinstance(communities, str):
            try:
                communities = json.loads(communities)
            except JSONDecodeError:
                communities = communities.split(",")
        for community_id in communities:
            community = Community.objects.get(community_id=community_id)
            CommunityPosts.objects.create(community=community, user=self.request.user, item=item_instance)
        return Response({"msg": "Item Uploaded Successfully in all communities"}, status=status.HTTP_200_OK)


class NetworkPostItemSessionCheckout(generics.CreateAPIView):
    serializer_class = NetworkPostItemSessionCheckoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            data = self.request.data
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            item_id = data.get("item_id")
            item = Items.objects.get(item_id=item_id)
            if item.public_bank:
                SECRET_KEY = item.public_bank.private_key
                WEBHOOK_SECRET = item.public_bank.webhook_key
            if item.private_bank:
                SECRET_KEY = item.private_bank.private_key
                WEBHOOK_SECRET = item.private_bank.webhook_key
            stripe.api_key = SECRET_KEY
            stripe.endpoint_secret = WEBHOOK_SECRET
            user = User.objects.get(email=self.request.user.email)
            total_price = float(data.get("total_price"))
            if total_price > 0:
                checkout_session = stripe.checkout.Session.create(
                    line_items=[
                        {
                            'price_data': {
                                'currency': 'usd',
                                'unit_amount': int(total_price * 100),
                                'product_data': {
                                    'name': item.title,
                                    'images': [item.image.url]
                                }
                            },
                            'quantity': 1,
                        },
                    ],
                    mode='payment',
                    metadata=dict({"data": str("test")}),
                    customer_email=user,
                    success_url=data.get("success_url"),
                    cancel_url=data.get("cancel_url"),
                )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(checkout_session)

class ChatbotAPIView(generics.ListCreateAPIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ChatbotAPIViewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.chatbots.all()

    def create(self, request, *args, **kwargs):
        data = self.request.data
        uploaded_file = data.get("file")
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)
            temp_file_path = Path(temp_file.name)
        client = OpenAI()
        # Use the saved file path with the OpenAI API
        file = client.files.create(
            file=temp_file_path,
            purpose="assistants"
        )
        # Optionally delete the temporary file after use
        temp_file_path.unlink()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user, file_id=file.id)

        run_in_thread(create_assistant, (file, serializer.data.get("chatbot_id")))

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SendWhatsappMessage(generics.CreateAPIView):
    pass


class WhatsappWebhook(generics.ListCreateAPIView):
    serializer_class = []
    # authentication_classes = [HMACAuthentication]

    @staticmethod
    def is_valid_whatsapp_message(body):
        """
        Check if the incoming webhook event has a valid WhatsApp message structure.
        """
        return (
                body.get("object")
                and body.get("entry")
                and body["entry"][0].get("changes")
                and body["entry"][0]["changes"][0].get("value")
                and body["entry"][0]["changes"][0]["value"].get("messages")
                and body["entry"][0]["changes"][0]["value"]["messages"][0]
        )

    def get(self, request, *args, **kwargs):
        # Parse params from the webhook verification request
        mode = request.query_params.get('hub.mode')
        token = request.query_params.get('hub.verify_token')
        return HttpResponse(request.GET.get('hub.challenge'), status=status.HTTP_200_OK)

        # if mode and token:
        #     # Check the mode and token sent are correct
        #     if mode == 'subscribe' and token == os.getenv("verify_token"):
        #         # Respond with 200 OK and challenge token from the request
        #         return HttpResponse(request.GET.get('hub.challenge'), status=status.HTTP_200_OK)
        #     else:
        #         # Responds with '403 Forbidden' if verify tokens do not match
        #         return HttpResponse("Verification failed", status=403)
        # else:
        #     # Responds with '400 Bad Request' if parameters are missing
        #     return HttpResponse("Verification failed", status=400)


    @staticmethod
    def get_text_message_input(recipient, text):
        return json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient,
                "type": "text",
                "text": {"preview_url": False, "body": text},
            }
        )

    def is_valid_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def random_password_generator(self, length):
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(characters) for i in range(length))
        return password

    def update_whatsapp_listing(self, user, title, description):
        # Define the default paths for image and video
        default_image_path = os.path.join(settings.BASE_DIR, 'logo.jpg')
        default_video_path = os.path.join(settings.BASE_DIR, 'item_video.mp4')
        category = Category.objects.create(title=title)

        Items.objects.create(
            vendor=user, listing=ListingType.WHATSAPP, title=title,
            description=description, price=10, category=category,
            image=default_image_path,  # Set default image path
            video=default_video_path  # Set default video path
        )

    def assign_room(self, user):
        if user.room is None:
            room = Room.objects.create(custom_instructions=False)
            user.room = room
            user.save()

    def get_openai_response(self, input_, phone_number_id, name, phone_no):
        client = OpenAI()
        configuration = WhatsappConfiguration.objects.filter(phone_no_id=phone_number_id).first()
        user = User.objects.filter(phone_no=phone_no)
        self.assign_room(user)
        if input_.upper() == "ROOM LOGIN":
            GeneralRoomLoginRequests.objects.filter(user=user).update(is_expired=True)
            room_request = GeneralRoomLoginRequests.objects.create(user=user)
            return f"Room Login OTP is: {room_request.otp}"

        if configuration:
            if not User.objects.filter(phone_no=phone_no).exists():
                try:
                    WhatsappAccountRequest.objects.get(phone_no=phone_no, account_created=True)
                except WhatsappAccountRequest.DoesNotExist:
                    account, created = WhatsappAccountRequest.objects.get_or_create(phone_no=phone_no)
                    if created:
                        message = ("Hi {} it looks like you you don't have account created with us "
                                   "please enter you email to create account".format(name))
                        return message
                    else:
                        if self.is_valid_email(input_):
                            created = False
                            if User.objects.filter(email=input_).exists():
                                user = User.objects.get(email=input_)
                                user.phone_no = phone_no
                                message = "Phone Number Updated Successfully"
                            else:
                                user = User.objects.create(email=input_, phone_no=phone_no, first_name=name)
                                message = "Account Created Successfully"
                                created = True
                            password = self.random_password_generator(16)
                            user.set_password(password)
                            user.save()
                            password_text = "Password" if created else "NewPassword"
                            WhatsappAccountRequest.objects.filter(phone_no=phone_no).update(account_created=True)
                            return ("{} \n"
                                    "Email: {} \n"
                                    "{}: {} \n"
                                    "Url: {}".format(message, input_, password_text, password, settings.DEPLOYED_HOST))
                        else:
                            return "Invalid Email Provided Please Enter Valid Email"

            else:
                file_id = configuration.chatbot.file_id
                thread = client.beta.threads.create()
                assistant_id = configuration.chatbot.assistant_id
                message = client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=input_,
                    file_ids=[file_id]
                )
                run = client.beta.threads.runs.create(
                    thread_id=thread.id,
                    assistant_id=assistant_id,
                    instructions="Please address the user as {}. The user has a premium account and do"
                                 " not mention anything about uploaded file".format(name)
                )
                # Wait for completion
                while run.status != "completed":
                    # Be nice to the API
                    time.sleep(0.5)
                    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
                messages = client.beta.threads.messages.list(thread_id=thread.id)
                response = messages.data[0].content[0].text.value
                if user.last():
                    ChatBotHistory.objects.create(
                        user=user.last(), chatbot=configuration.chatbot, query=input_, response=response)
                run_in_thread(self.update_whatsapp_listing, (user, input_, response))
                return response

        response = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=input_,
            max_tokens=int(500),
            stop=None,
        )
        for object in response:
            if "choices" in object:
                response2 = object[1][0]
                for object2 in response2:
                    if "text" in object2:
                        result = object2[1]

        run_in_thread(self.update_whatsapp_listing, (user, input_, result))
        return result

    def send_message(self, data1, body, client_phone_no, name):
        data1 = json.loads(data1)
        phone_no = data1["to"]
        res = self.get_openai_response(body, client_phone_no, name, phone_no)
        headers = {
            "Content-type": "application/json",
            "Authorization": "Bearer {}".format(os.getenv("access_token")),
        }
        url = "https://graph.facebook.com/v19.0/291096477411186/messages"
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_no,
            "type": "text",
            "text":
                {
                    "preview_url": False,
                    "body": res
                }
        }

        try:
            response = requests.post(
                url, data=json.dumps(data), headers=headers, timeout=10
            )
        except requests.Timeout:
            return Response({"status": "error", "message": "Request timed out"}), 408
        except Exception as e:
            return Response({"status": "error", "message": "Failed to send message"}), 500
        else:
            return response

    def process_whatsapp_message(self, body):
        print(body)
        wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
        name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]

        message = body["entry"][0]["changes"][0]["value"]["messages"][0]
        client_phone_no = body["entry"][0]["changes"][0]["value"]["metadata"]["phone_number_id"]
        message_body = message["text"]["body"]
        data = self.get_text_message_input(wa_id, message)
        self.send_message(data, message_body, client_phone_no, name)

    def post(self, request, *args, **kwargs):
        try:
            body = self.request.data
            if self.is_valid_whatsapp_message(body):
                self.process_whatsapp_message(body)
                return Response({"status": "ok"}, status=status.HTTP_200_OK)
            else:
                # if the request is not a WhatsApp API event, return an error
                return Response(
                    {"status": "error", "message": "Not a WhatsApp API event"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        except json.JSONDecodeError:
            return Response(
                {"status": "error", "message": "Invalid JSON provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ChatbotDelUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ChatbotAPIViewSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return Chatbots.objects.get(
                chatbot_id=self.request.query_params.get("chatbot_id", None), user=self.request.user)
        except Exception as e:
            raise ValidationError({"error": str(e)})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        serializer = self.get_serializer(self.get_object(), data=self.request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response({"msg": "Chatbot Deleted Successfully"})


class WhatsappConfigurationView(generics.ListCreateAPIView):
    serializer_class = WhatsappConfigurationSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = self.request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        chatbot = data.get("chatbot", None)
        chatbot = Chatbots.objects.get(chatbot_id=str(chatbot))
        serializer.save(chatbot=chatbot)
        return Response({"msg": "Chatbot Integrated with whatsapp successfully"}, status=status.HTTP_201_CREATED)


def DumpItems(request):
    # Query all items from the Items table
    items = Items.objects.all()

    # Create a BytesIO buffer to hold the PDF
    buffer = BytesIO()

    # Create a new PDF document
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Define styles for the PDF
    styles = getSampleStyleSheet()
    question_style = styles["Heading1"]
    answer_style = styles["Normal"]

    # Iterate through each item
    for item in items:
        # Add the title as a question
        elements.append(Paragraph(f"<u>{item.title}</u>", question_style))

        # Add the rest of the item's data as the answer
        item_data = [
            ["Vendor Email:", item.vendor_email],
            ["Category:", item.category.title],
            ["Description:", item.description],
            ["Price:", f"${item.price}"],
            ["Location:", item.location],
            ["Stock:", str(item.stock)],
            ["Image:", str(item.image.url)] if item.image else [],
            ["qr_code:", str(item.qr_code.url)],
        ]

        # Add the item data as a table
        table = Table(item_data, colWidths=[100, 300])
        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey)]))
        elements.append(table)

        # Add spacing between items
        elements.append(Paragraph("<br/><br/>", answer_style))

    # Build the PDF document
    pdf.build(elements)

    # Get the value of the BytesIO buffer and reset the buffer
    pdf_data = buffer.getvalue()
    buffer.close()

    # Create an HTTP response with the PDF data
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="items_data.pdf"'
    response.write(pdf_data)
    return response