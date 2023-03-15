import os
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
import speech_recognition as sr
import openai
from django.views.decorators.csrf import csrf_exempt

from engine.models import ResponsesDB, VoiceToVoiceRequests, ImagesDB, ShopAccess
from users.models import User


openai.api_key = os.getenv("OPEN_AI_KEY")


def HomepageView(request):
    return render(request, "homepage.html")


def Logout(request):
    logout(request)
    return redirect('HomepageView')


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
    images_generated = 0
    is_active = True
    for image in request.user.images.all():
        images_generated += len(image.images)
    if request.user.premium == 0 and images_generated >= 10:
        is_active = False
    if request.user.premium == 1 and images_generated >= 30:
        is_active = False
    return render(request, "chat.html", context={"is_active": is_active})


def ShopVoiceToVoice(request):
    shop = ShopAccess.objects.all().first()
    if shop.switch:
        return render(request, "ShopVoiceToVoice.html")
    else:
        return render(request, "404.html")


def VoiceToVoice(request):
    is_active = True
    try:
        obj = VoiceToVoiceRequests.objects.get(user=request.user)
        if obj.user.premium == 0:
            if obj.requests_send >= 20:
                is_active = False
        if obj.user.premium == 1:
            if obj.requests_send >= 100:
                is_active = False
        context = {
            "is_active": is_active,
        }
        return render(request, "voice_to_voice.html", context=context)
    except Exception as e:
        context = {
            "is_active": is_active
        }
        return render(request, "voice_to_voice.html", context=context)


@csrf_exempt
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
    response = ImagesDB.objects.filter(question__icontains=text)
    if not response:
        response = openai.Image.create(prompt="{}".format(text), n=3, size="1024x1024")
        images = list()
        for image in response['data']:
            images.append(image.url)
        if request.user.is_authenticated:
            ImagesDB.objects.create(question=text, images=images, user=request.user)
        else:
            ImagesDB.objects.create(question=text, images=images, user=request.user)
        return JsonResponse(images, safe=False)
    else:
        return JsonResponse(response.last().images, safe=False)


def get_chatgpt_response(request):
    try:
        obj = VoiceToVoiceRequests.objects.get(user=request.user)
        obj.requests_send += 1
        obj.save()
    except Exception as e:
        VoiceToVoiceRequests.objects.create(user=request.user, requests_send=1)
    prompt = request.GET.get('text', '')
    response = ResponsesDB.objects.filter(question__icontains=prompt)
    if not response:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a chatbot"},
                {"role": "user", "content": "{}?".format(prompt)},
            ]
        )

        result = ''
        for choice in response.choices:
            result += choice.message.content
        ResponsesDB.objects.create(question=prompt, answer=result)
        return HttpResponse(str(result))
    else:
        return HttpResponse(str(response.last().answer))


def TextToText(request):
    return render(request, "TextToText.html")

