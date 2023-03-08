import os

from django.contrib.auth import authenticate, login
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
import speech_recognition as sr
import openai
from users.models import User

openai.api_key = os.getenv("OPEN_AI_KEY", "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")


def HomepageView(request):
    return render(request, "homepage.html")


def LoginView(request):
    if request.method == "POST":
        try:
            email = request.POST.get("email")
            password = request.POST.get("password")
            user = User.objects.get(email=email)
            user_auth = authenticate(email=email, password=password)
            if user_auth is not None:
                login(request, user)
                return redirect("/")
            else:
                redirect('/api/login/')

        except User.DoesNotExist:
            redirect('/api/login/')
    return render(request, "login.html")


def RegisterView(request):
    """
    Create a user
    {
        "email": "bob_marley@gmail.com",
        "first_name": "Bob",
        "last_name": "Marley",
    }
    """
    if request.method == "POST":
        try:
            fname = request.POST.get("fname")
            lname = request.POST.get("lname")
            email = request.POST.get("email")
            password = request.POST.get("password")
            user = User.objects.create(first_name=fname, last_name=lname, email=email)
            user.set_password(password)
            user.save()
            return redirect('/api/login/')
        except IntegrityError as e:
            redirect('/api/register/')
    return render(request, "register.html")


def VoiceToImage(request):
    return render(request, "chat.html")


def VoiceOutPut(request):
    filename = "test" + "name" + ".wav"
    uploadedFile = open(filename, "wb")
    # the actual file is in request.body
    uploadedFile.write(request.body)
    uploadedFile.close()
    # put additional logic like creating a model instance or something like this here
    r = sr.Recognizer()
    harvard = sr.AudioFile(filename)
    with harvard as source:
        audio = r.record(source)
    msg = r.recognize_google(audio)

    return HttpResponse("{}".format(msg))


def UploadVoice(request):
    text = request.GET.get('text', '')
    no_of_images = request.GET.get('no_of_images', '')
    response = openai.Image.create(prompt="{}".format(text), n=int(no_of_images), size="1024x1024")
    images = list()
    for image in response['data']:
        images.append(image.url)
    return JsonResponse(images, safe=False)