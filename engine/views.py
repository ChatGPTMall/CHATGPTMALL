import ast
import os
import openai
import stripe
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework import generics, status
from rest_framework.response import Response
# Create your views here.
from engine.serializers import TextToTexTViewSerializer
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
