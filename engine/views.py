import os
import ast
import openai
import stripe
import requests
from io import BytesIO
from urllib.request import urlopen
from django.core.files import File
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework import generics, status
from rest_framework.response import Response
from engine.models import ImagesDB
from engine.serializers import TextToTexTViewSerializer, ImageAnalysisViewSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from users.models import User

openai.api_key = os.getenv("OPEN_AI_KEY")
stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET


class TextToTexTView(generics.CreateAPIView):
    serializer_class = TextToTexTViewSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
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
