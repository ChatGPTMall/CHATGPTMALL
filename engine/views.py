import base64
import json
import os
import ast
import urllib
from json import JSONDecodeError

import openai
import stripe
import requests
from io import BytesIO

from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema

from django.core.files.base import ContentFile
from drf_spectacular.utils import extend_schema
from openai import OpenAI
from engine.permissions import HaveCredits
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
    BankAccounts, CouponCode
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from engine.serializers import TextToTexTViewSerializer, ImageAnalysisViewSerializer, ShopItemsViewSerializer, \
    ShopCategoriesViewSerializer, GetItemsViewSerializer, TextToTexTMicrosoftViewSerializer, TranscribeAudioSerializer, \
    TextToTexTViewImageSerializer, VisionViewSerializer

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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(vendor=self.request.user, vendor_email=self.request.user.email)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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


class ItemPurchases(generics.ListCreateAPIView):
    serializer_class = ItemPurchasesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.user_purchases.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user=self.request.user, buyer_email=self.request.user.email,
            purchase_date=timezone.now())
        return Response(serializer.data, status=status.HTTP_201_CREATED)
