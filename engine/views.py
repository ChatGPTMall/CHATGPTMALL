import os
import openai
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
# Create your views here.
from engine.serializers import TextToTexTViewSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny

openai.api_key = os.getenv("OPEN_AI_KEY")


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