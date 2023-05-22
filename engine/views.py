import os
import ast
import urllib
import openai
import stripe
import requests
from io import BytesIO
from users.models import User
from django.urls import reverse
from django.conf import settings
from django.core.files import File
from urllib.request import urlopen
from rest_framework import generics, status
from PIL import Image, ImageDraw, ImageFont
from rest_framework.response import Response
from django.shortcuts import render, redirect
from engine.models import ImagesDB, ImageAnalysisDB, Items, Category
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from engine.serializers import TextToTexTViewSerializer, ImageAnalysisViewSerializer, ShopItemsViewSerializer, \
    ShopCategoriesViewSerializer, GetItemsViewSerializer, TextToTexTMicrosoftViewSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET


class TextToTexTView(generics.CreateAPIView):
    serializer_class = TextToTexTViewSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        openai.api_key = os.getenv("OPEN_AI_KEY")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        input = request.data["input"]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a chatbot"},
                {"role": "user", "content": "{}?".format(input)},
            ]
        )

        result = ''
        for choice in response.choices:
            result += choice.message.content
        return Response(dict({
            "input": input,
            "response": result
        }), status=status.HTTP_201_CREATED)


class TextToTexTOpeniaiView(generics.CreateAPIView):
    serializer_class = TextToTexTViewSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            api_key = request.query_params.get("openai_key", None)
            if api_key is None:
                return Response({"error": "openai_key API Key is Required"}, status=status.HTTP_400_BAD_REQUEST)
            openai.api_key = api_key
            input_ = request.data["input"]
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a chatbot"},
                    {"role": "user", "content": "{}?".format(input_)},
                ]
            )

            result = ''
            for choice in response.choices:
                result += choice.message.content
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
                prompt=input_,
            )
            text = response['choices'][0]['text'].replace('\n', '').replace(' .', '.').strip()
            return Response(dict({
                "input": input_,
                "response": text
            }), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TextToImageView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TextToTexTViewSerializer

    def post(self, request, *args, **kwargs):
        URL = os.getenv("DEPLOYED_HOST", "https://madeinthai.org")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        input = request.data["input"]
        res = ImagesDB.objects.filter(question__icontains=input)
        if not res:
            response = openai.Image.create(prompt="{}".format(input), n=3, size="1024x1024")
            images = list()
            for image in response['data']:
                images.append(image.url)
            imagedb = ImagesDB.objects.create(question=input, user=self.request.user)
            response1 = urlopen(images[0])
            io1 = BytesIO(response1.read())
            imagedb.image1.save("image_one.jpg", File(io1))

            response2 = urlopen(images[1])
            io2 = BytesIO(response2.read())
            imagedb.image2.save("image_two.jpg", File(io2))

            response3 = urlopen(images[2])
            io3 = BytesIO(response3.read())
            imagedb.image3.save("image_three.jpg", File(io3))

            show_images = list()

            show_images.append(URL+imagedb.image1.url)
            show_images.append(URL+imagedb.image2.url)
            show_images.append(URL+imagedb.image3.url)
        else:
            show_images = list()
            show_images.append(URL + res.last().image1.url)
            show_images.append(URL + res.last().image2.url)
            show_images.append(URL + res.last().image3.url)
        return Response(dict({
            "input": input,
            "images": show_images
        }), status=201)


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
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category, created = Category.objects.get_or_create(title=request.data["category"])
        if not Items.objects.filter(title=request.data["title"]).exists():
            item = Items.objects.create(
                title=request.data["title"], description=request.data["description"],
                image=request.data['image'], category=category)
            URL = os.getenv("DEPLOYED_HOST", "https://madeinthai.org")
            return Response({
                "item_id": item.id,
                "category_id": category.id,
                "category_title": category.title,
                "title": item.title,
                "description": item.description,
                "image": URL + item.image.url,
                "added_on": item.added_on,
                "updated_on": item.updated_on
            }, status=status.HTTP_201_CREATED)
        return Response({"error": "item already exists"}, status=status.HTTP_400_BAD_REQUEST)


class GetItemsView(generics.ListAPIView):
    serializer_class = GetItemsViewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Items.objects.all()


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
