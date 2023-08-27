import base64
import json
import os
import random
import urllib
from io import BytesIO
from io import BytesIO as IO
from urllib.request import urlopen
import requests
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
import openai
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from django.core.files.uploadedfile import InMemoryUploadedFile
from msrest.authentication import CognitiveServicesCredentials
from array import array
import os
from PIL import Image
import sys
import time
import qrcode
from django.core import files
from django.core.files import File
from django.core.mail import send_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
import pandas as pd
from users.models import User
import speech_recognition as sr
from django.db import IntegrityError
from django.shortcuts import render, redirect
from rest_framework.authtoken.models import Token
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from engine.models import ResponsesDB, VoiceToVoiceRequests, ImagesDB, ShopAccess, Plans, Industries, Capabilities, \
    Jobs, Community, CommunityMembers, CommunityPosts, CouponCode, Subscriptions, Items, ImageAnalysisDB, Category, \
    VoiceCommands, KeyManagement, FreeSubscriptions, CapturedImages


# openai.api_key = os.getenv("OPEN_AI_KEY")


def HomepageView(request):
    show_logo = False
    DEPLOYED_HOST = os.getenv("DEPLOYED_HOST", None)
    if DEPLOYED_HOST == "https://madeinthai.org":
        show_logo = True
    key = KeyManagement.objects.all().last()
    return render(request, "homepage.html", context={"show_logo": show_logo, "key": key})


def AiModels(request):
    show_logo = False
    DEPLOYED_HOST = os.getenv("DEPLOYED_HOST", None)
    if DEPLOYED_HOST == "https://madeinthai.org":
        show_logo = True
    key = KeyManagement.objects.all().last()
    return render(request, "homepage2.html", context={"show_logo": show_logo, "key": key})

def Logout(request):
    logout(request)
    return redirect('HomepageView')


def LoginView(request):
    page = request.GET.get("page", None)
    if request.method == "POST":
        try:
            email = request.POST.get("email")
            password = request.POST.get("password")
            user = User.objects.get(email=email)
            user_auth = authenticate(email=email, password=password)
            if user_auth is not None:
                login(request, user)
                Token.objects.get_or_create(user=user)
                if page and page != "None":
                    return redirect("/" + page)
                return redirect("/")
            else:
                redirect('/api/login/')

        except User.DoesNotExist:
            redirect('/api/login/')
    return render(request, "login.html", {"page": page})


def RegisterView(request):
    """
    Create a user
    {
        "email": "bob_marley@gmail.com",
        "first_name": "Bob",
        "last_name": "Marley",
    }
    """
    page = request.GET.get("page", None)
    if request.method == "POST":
        try:
            fname = request.POST.get("fname")
            lname = request.POST.get("lname")
            email = request.POST.get("email")
            password = request.POST.get("password")
            user = User.objects.create(first_name=fname, last_name=lname, email=email)
            user.set_password(password)
            user.save()
            subject = "Chatgptmall Account Created"
            message = "Congratulations {} you are successfully registered on CHATGPTMALL".format(user.get_full_name())
            send_mail(subject=subject, message=message, from_email=settings.EMAIL_HOST_USER,
                      recipient_list=[email], fail_silently=True)
            if page and page != "None":
                user_auth = authenticate(email=email, password=password)
                if user_auth is not None:
                    login(request, user)
                    Token.objects.get_or_create(user=user)
                return redirect("/" + page)
            return redirect('/api/login/')
        except IntegrityError as e:
            redirect('/api/register/')
    return render(request, "register.html", {"page": page})


def ProfileView(request):
    if request.user.is_authenticated:
        plans = []
        for plan in request.user.purchases.all():
            added_on = plan.added_on
            title = plan.plan.title
            left = plan.plan.requests - plan.requests_send
            left = 0 if left < 0 else left
            plans.append({
                "added_on": added_on,
                "title": title,
                "requests": plan.requests_send,
                "requests_left": left,
            })
        return render(request, "profile.html", context={"plans": plans})
    return redirect('/api/login/')


def ProfileUpdate(request):
    request.user.first_name = request.POST.get("first_name")
    request.user.last_name = request.POST.get("last_name")
    request.user.address = request.POST.get("address")
    request.user.city = request.POST.get("city")
    request.user.country = request.POST.get("country")
    request.user.postal_code = request.POST.get("postal_code")
    request.user.save()
    return redirect("/api/profile/")


def VoiceToImage(request):
    if request.user.is_authenticated:
        text = request.GET.get("item", None)
        if request.user.premium == 1:
            if Subscriptions.objects.filter(user=request.user, plan__access="VOICE_TO_IMAGE", is_expired=False).exists():
                return render(request, "chat.html", context={"text": text})
            return redirect('/api/renew/subscription/')
        return render(request, "chat.html", context={"text": text})
    return redirect(reverse("LoginView") + "?page={}".format("models/voice_to_image/detail/"))


def TextToVoice(request):
    if request.user.is_authenticated:
        text = request.GET.get("item", None)
        if request.user.premium == 1:
            if Subscriptions.objects.filter(user=request.user, plan__access="TEXT_TO_VOICE", is_expired=False).exists():
                return render(request, "text_to_voice.html", context={"text": text})
            return redirect('/api/renew/subscription/')
        return render(request, "text_to_voice.html", context={"text": text})
    return redirect(reverse("LoginView") + "?page={}".format("models/Text_to_voice/detail/"))


def ShopVoiceToVoice(request):
    shop = ShopAccess.objects.all().first()
    if shop.switch:
        return render(request, "ShopVoiceToVoice.html")
    else:
        return render(request, "404.html")


def VoiceToVoice(request):
    if request.user.is_authenticated:
        text = request.GET.get("item", None)
        if request.user.premium == 1:
            if Subscriptions.objects.filter(user=request.user, plan__access="VOICE_TO_Voice", is_expired=False).exists():
                return render(request, "voice_to_voice.html", context={"text": text})
            return redirect('/api/renew/subscription/')
        return render(request, "voice_to_voice.html", context={"text": text})
    return redirect(reverse("LoginView") + "?page={}".format("models/voice_to_voice/detail/"))


def GetCommand(request):
    if request.user.is_authenticated:
        text = request.GET.get("item", None)
        if request.user.premium == 1:
            if Subscriptions.objects.filter(user=request.user, plan__access="VOICE_TO_COMMAND", is_expired=False).exists():
                return render(request, "voice_to_command.html", context={"text": text})
            return redirect("/api/renew/subscription/")
        return render(request, "voice_to_command.html", context={"text": text})
    return redirect(reverse("LoginView") + "?page={}".format("models/voice_to_command/detail/"))


def TextToCommand(request):
    if request.user.is_authenticated:
        text = request.GET.get("item", None)
        if request.user.premium == 1:
            if Subscriptions.objects.filter(user=request.user, plan__access="TEXT_TO_COMMAND", is_expired=False).exists():
                return render(request, "text_to_command.html", context={"text": text})
            return redirect("/api/renew/subscription/")
        return render(request, "text_to_command.html", context={"text": text})
    return redirect(reverse("LoginView") + "?page={}".format("models/text_to_command/detail/"))


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
    try:
        img = request.GET.get('img', None)
        if img:
            plan__access = "TEXT_TO_IMAGE"
        else:
            plan__access = "VOICE_TO_IMAGE"
        if request.user.premium == 1:
            plan = Plans.objects.filter(access=plan__access).last()
            obj, created = Subscriptions.objects.get_or_create(user=request.user, plan=plan)
            obj.requests_send += 1
            obj.save()
            if obj.requests_send >= obj.plan.requests:
                obj.is_expired = True
                obj.save()
        if request.user.premium == 0:
            plan = Plans.objects.filter(access=plan__access).last()
            obj, create = FreeSubscriptions.objects.get_or_create(user=request.user, plan=plan)
            obj.requests_send += 1
            obj.save()
            if obj.requests_send >= obj.plan.free_requests:
                obj.is_expired = True
                obj.save()
    except Exception as e:
        pass
    text = request.GET.get('text', '')
    response = ImagesDB.objects.filter(question__icontains=text)
    if not response:
        key = KeyManagement.objects.all().last()
        if key:
            openai.api_key = key.key
            resp = openai.Image.create(prompt="{}".format(text), n=3, size="1024x1024")
            print(resp)
            images = list()
            for image in resp['data']:
                images.append(image.url)
            if request.user.is_authenticated:
                imagedb = ImagesDB.objects.create(question=text, user=request.user)
            else:
                ImagesDB.objects.create(question=text, images=images)
            print(images)
            # response1 = urlopen(images[0])
            response1 = requests.get(images[0])
            original_image = Image.open(BytesIO(response1.content))
            print(original_image)
            # Resize the image
            resized_image = original_image.resize((300, 300))  # Specify the desired dimensions

            # Save the resized image to a buffer
            image_buffer = BytesIO()
            resized_image.save(image_buffer, format='JPEG')
            image_buffer.seek(0)
            print(image_buffer)

            # io1 = BytesIO(response1.read())
            imagedb.image1.save("image_one.jpg", image_buffer)
            print("save 1")

            # response2 = urlopen(images[1])
            # io2 = BytesIO(response2.read())
            response1 = requests.get(images[0])
            original_image2 = Image.open(BytesIO(response1.content))
            # Resize the image
            resized_image2 = original_image2.resize((300, 300))  # Specify the desired dimensions

            # Save the resized image to a buffer
            image_buffer2 = BytesIO()
            resized_image2.save(image_buffer2, format='JPEG')
            image_buffer2.seek(0)
            imagedb.image2.save("image_two.jpg", image_buffer2)

            # response3 = urlopen(images[2])
            # io3 = BytesIO(response3.read())
            response3 = requests.get(images[0])
            original_image3 = Image.open(BytesIO(response3.content))
            # Resize the image
            resized_image3 = original_image3.resize((300, 300))  # Specify the desired dimensions

            # Save the resized image to a buffer
            image_buffer3 = BytesIO()
            resized_image3.save(image_buffer3, format='JPEG')
            image_buffer3.seek(0)
            imagedb.image3.save("image_three.jpg", image_buffer3)

            show_images = list()

            show_images.append(imagedb.image1.url)
            show_images.append(imagedb.image2.url)
            show_images.append(imagedb.image3.url)

            return JsonResponse(show_images, safe=False)
    else:
        show_images = list()
        show_images.append(response.last().image1.url)
        show_images.append(response.last().image2.url)
        show_images.append(response.last().image3.url)
        return JsonResponse(show_images, safe=False)


def ResponseCommand(request):
    text = request.GET.get('text', '')
    try:
        command = request.GET.get('command', '')
        if command == "voice":
            plan_access = "VOICE_TO_COMMAND"
        else:
            plan_access = "TEXT_TO_COMMAND"
        print(plan_access)
        command = VoiceCommands.objects.get(input=text)
        if request.user.premium == 1:
            plan = Plans.objects.filter(access=plan_access).last()
            obj, created = Subscriptions.objects.get_or_create(user=request.user, plan=plan)
            obj.requests_send += 1
            obj.save()
            if obj.requests_send >= obj.plan.requests:
                obj.is_expired = True
                obj.save()
        if request.user.premium == 0:
            plan = Plans.objects.filter(access=plan_access).last()
            obj, create = FreeSubscriptions.objects.get_or_create(user=request.user, plan=plan)
            obj.requests_send += 1
            obj.save()
            if obj.requests_send >= obj.plan.free_requests:
                obj.is_expired = True
                obj.save()
        return HttpResponse(command.image.url)
    except Exception as e:
        return HttpResponse("invalid")


def GetImages(request):
    pass


def get_chatgpt_response(request):
    try:
        words = request.GET.get('words', None)
        page = request.GET.get('page', None)
        if words:
            plan__access = "TEXT_TO_TEXT"
        else:
            plan__access = "VOICE_TO_Voice"
            words = 2000
        if page == "voice_to_text":
            plan__access = "TEXT_TO_VOICE"
        if request.user.premium == 1:
            plan = Plans.objects.filter(access=plan__access).last()
            obj, created = Subscriptions.objects.get_or_create(user=request.user, plan=plan)
            obj.requests_send += 1
            obj.save()
            if obj.requests_send >= obj.plan.requests:
                obj.is_expired = True
                obj.save()
        if request.user.premium == 0:
            plan = Plans.objects.filter(access=plan__access).last()
            obj, create = FreeSubscriptions.objects.get_or_create(user=request.user, plan=plan)
            obj.requests_send += 1
            obj.save()
            if obj.requests_send >= obj.plan.free_requests:
                obj.is_expired = True
                obj.save()
    except Exception as e:
        print(e)
        words = request.GET.get('words', None)
    prompt = request.GET.get('text', '')
    response = ResponsesDB.objects.filter(question__icontains=prompt)
    if not response:
        key = KeyManagement.objects.all().last()
        if key:
            openai.api_key = key.key
            if key.platform == "MICROSOFT":
                openai.api_base = "{}".format(key.endpoint)
                openai.api_type = 'azure'
                openai.api_version = "2023-03-15-preview"
                model = "davinci"
                response = openai.Completion.create(
                    engine=model,
                    max_tokens=int(words),
                    prompt=prompt,
                )
                text = response['choices'][0]['text'].replace('\n', '').replace(' .', '.').strip()
                ResponsesDB.objects.create(question=prompt, answer=text)
                return HttpResponse(str(text))
            else:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    max_tokens=3000,
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


def get_text(request):
    prompt = request.GET.get('text', '')
    key = KeyManagement.objects.all().last()
    openai.api_key = key.key
    if key.platform == "MICROSOFT":
        openai.api_base = "{}".format(key.endpoint)
        openai.api_type = 'azure'
        openai.api_version = "2023-03-15-preview"
        model = "davinci"
        response = openai.Completion.create(
            engine=model,
            max_tokens=int(2000),
            prompt=prompt,
        )
        text = response['choices'][0]['text'].replace('\n', '').replace(' .', '.').strip()
        return HttpResponse(str(text))
    else:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            max_tokens=int(2000),
            messages=[
                {"role": "system", "content": "You are a chatbot"},
                {"role": "user", "content": "{}?".format(prompt)},
                ]
        )
        result = ''
        for choice in response.choices:
            result += choice.message.content

        return HttpResponse(str(result))


def get_image(request):
    prompt = request.GET.get('text', '')
    openai.api_key = os.getenv("OPEN_AI_KEY")
    resp = openai.Image.create(prompt="{}".format(prompt), n=1, size="1024x1024")
    images = list()
    for image in resp['data']:
        images.append(image.url)
    return HttpResponse(str(images[0]))


def TextToText(request):
    if request.user.is_authenticated:
        text = request.GET.get("item", None)
        communities = list()
        if CommunityMembers.objects.filter(user=request.user).exists():
            communities_id = request.user.team.all().values_list("community__community_id", flat=True)
            communities = Community.objects.filter(community_id__in=communities_id)
        if request.user.premium == 1:
            if Subscriptions.objects.filter(user=request.user, plan__access="TEXT_TO_TEXT", is_expired=False).exists():
                return render(request, "TextToText.html", context={"communities": communities, "text": text})
            return redirect('/api/renew/subscription/')
        return render(request, "TextToText.html", context={"text": text, "communities": communities})
    return redirect(reverse("LoginView") + "?page={}".format("models/text_to_text/detail/"))


def TextToImage(request):
    if request.user.is_authenticated:
        text = request.GET.get("item", None)
        communities = list()
        if CommunityMembers.objects.filter(user=request.user).exists():
            communities_id = request.user.team.all().values_list("community__community_id", flat=True)
            communities = Community.objects.filter(community_id__in=communities_id)
        if request.user.premium == 1:
            if Subscriptions.objects.filter(user=request.user, plan__access="TEXT_TO_IMAGE", is_expired=False).exists():
                return render(request, "TextToImage.html", context={"communities": communities, "text": text})
            return redirect('/api/renew/subscription/')
        return render(request, "TextToImage.html", context={"text": text, "communities": communities})
    return redirect(reverse("LoginView") + "?page={}".format("models/text_to_image/detail/"))


def ImageToImage(request):
    if request.user.is_authenticated:
        text = request.GET.get("item", None)
        if request.user.premium == 1:
            if Subscriptions.objects.filter(user=request.user, plan__access="Image_To_Text", is_expired=False).exists():
                return render(request, "imagetoimage.html")
            return redirect('/api/renew/subscription/', context={"text": text})
        return render(request, "imagetoimage.html", context={"text": text})
    return redirect(reverse("LoginView") + "?page={}".format("models/image_to_image/detail/"))


def ImageToText(request):
    if request.user.is_authenticated:
        text = request.GET.get("item", None)
        if request.user.premium == 1:
            if Subscriptions.objects.filter(user=request.user, plan__access="Image_To_Text", is_expired=False).exists():
                return render(request, "imagetotext.html")
            return redirect('/api/renew/subscription/', context={"text": text})
        return render(request, "imagetotext.html", context={"text": text})
    return redirect(reverse("LoginView") + "?page={}".format("models/image_to_text/detail/"))


def ImageToImageCalculate(request):
    try:
        if request.user.premium == 1:
            plan = Plans.objects.filter(access="IMAGE_TO_IMAGE").last()
            obj, created = Subscriptions.objects.get_or_create(user=request.user, plan=plan)
            obj.requests_send += 1
            obj.save()
            if obj.requests_send >= obj.plan.requests:
                obj.is_expired = True
                obj.save()
        if request.user.premium == 0:
            plan = Plans.objects.filter(access="IMAGE_TO_IMAGE").last()
            obj, create = FreeSubscriptions.objects.get_or_create(user=request.user, plan=plan)
            obj.requests_send += 1
            obj.save()
            if obj.requests_send >= obj.plan.free_requests:
                obj.is_expired = True
                obj.save()
        return HttpResponse("IMAGE UPDATED")
    except Exception as e:
        return HttpResponse("IMAGE UPDATED")


def ImageAnalysis(request):
    if request.user.is_authenticated:
        text = request.GET.get("item", None)
        if request.user.premium == 1:
            if Subscriptions.objects.filter(user=request.user, plan__access="IMAGE_ANALYSIS", is_expired=False).exists():
                return render(request, "imageanalysis.html", context={"text": text})
            return redirect("/api/renew/subscription/")
        return render(request, "imageanalysis.html", context={"text": text})
    return redirect(reverse("LoginView") + "?page={}".format("models/text_analysis/detail/"))


def VideoAnalysis(request):
    # if Subscriptions.objects.filter(user=request.user, plan__access="VIDEO_ANALYSIS", is_expired=False).exists():
    # return redirect("/api/login/")
    return render(request, "videoanalysis.html")


def ObjectsDetection(request):
    if request.user.is_authenticated:
        text = request.GET.get("item", None)
        if request.user.premium == 1:
            if Subscriptions.objects.filter(user=request.user, plan__access="OBJECTS_DETECTION", is_expired=False).exists():
                communities = []
                if CommunityMembers.objects.filter(user=request.user).exists():
                    communities_id = request.user.team.all().values_list("community__community_id", flat=True)
                    communities = Community.objects.filter(community_id__in=communities_id)
                return render(request, "ObjectsDetection.html", context={"communities": communities, "text": text})
            return redirect("/api/renew/subscription/")
        return render(request, "ObjectsDetection.html", context={"text": text})
    return redirect(reverse("LoginView") + "?page={}".format("models/image_detect/detail/"))


@csrf_exempt
def SaveAnalysisImage(request):
    img = ImageAnalysisDB.objects.create(file=request.FILES.get("image"))
    try:
        if request.user.premium == 1:
            plan = Plans.objects.filter(access="IMAGE_ANALYSIS").last()
            obj, created = Subscriptions.objects.get_or_create(user=request.user, plan=plan)
            obj.requests_send += 1
            obj.save()
            if obj.requests_send >= obj.plan.requests:
                obj.is_expired = True
                obj.save()
        if request.user.premium == 0:
            plan = Plans.objects.filter(access="IMAGE_ANALYSIS").last()
            obj, create = FreeSubscriptions.objects.get_or_create(user=request.user, plan=plan)
            obj.requests_send += 1
            obj.save()
            if obj.requests_send >= obj.plan.free_requests:
                obj.is_expired = True
                obj.save()
    except Exception as e:
        pass
    return HttpResponse(str(img.file.url))

@csrf_exempt
def GetOcrImage(request):
    img = ImageAnalysisDB.objects.create(file=request.FILES.get("image"))
    try:
        if request.user.premium == 1:
            plan = Plans.objects.filter(access="Image_To_Text").last()
            obj, created = Subscriptions.objects.get_or_create(user=request.user, plan=plan)
            obj.requests_send += 1
            obj.save()
            if obj.requests_send >= obj.plan.requests:
                obj.is_expired = True
                obj.save()
        if request.user.premium == 0:
            plan = Plans.objects.filter(access="Image_To_Text").last()
            obj, create = FreeSubscriptions.objects.get_or_create(user=request.user, plan=plan)
            obj.requests_send += 1
            obj.save()
            if obj.requests_send >= obj.plan.free_requests:
                obj.is_expired = True
                obj.save()
    except Exception as e:
        pass
    subscription_key = "B0faa09900954b4ab9eee55e133399cc"
    endpoint = "https://bennyocr.cognitiveservices.azure.com/"
    computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
    read_response = computervision_client.read(str(img.file.url), raw=True)
    # Get the operation location (URL with an ID at the end) from the response
    read_operation_location = read_response.headers["Operation-Location"]
    # Grab the ID from the URL
    operation_id = read_operation_location.split("/")[-1]

    # Call the "GET" API and wait for it to retrieve the results
    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)
    response = ""
    # Print the detected text, line by line
    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                response += line.text + "\n"

    return HttpResponse(str(response))


@csrf_exempt
def OCRContentGenerate(request):
    user_input = request.POST.get('input', '')
    data = request.POST.get('data', '')
    prompt = user_input + data
    openai.api_key = os.getenv("OPEN_AI_KEY")
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
    return HttpResponse(str(result))


@csrf_exempt
def AnalysisVideo(request):
    pass

@csrf_exempt
def ObjDetect(request):
    img = ImageAnalysisDB.objects.create(file=request.FILES.get("image"))
    image = Image.open(img.file)
    url = "https://microsoft-computer-vision3.p.rapidapi.com/detect"
    payload = {
        "url": str(img.file.url)
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
        shape = [(left, top), (left + width, top+height)]
        image_draw.rectangle(shape, outline='blue', width=3)
        text = f'{obj["object"]} ({obj["confidence"] * 100}%)'
        image_draw.text((left + 5 - 1, top + height - 30 + 1), text, (0, 0, 0))
        image_draw.text((left + 5, top + height - 30), text, (255, 0, 0))
    blob = BytesIO()
    image.save(blob, 'JPEG')
    final_image = ImageAnalysisDB.objects.create(file=File(blob))
    final_image.file.save("test.png", File(blob))
    data = dict({
        "url2": payload["url"],
        "url": str(final_image.file.url),
        "results": results
    })
    try:
        if request.user.premium == 1:
            plan = Plans.objects.filter(access="OBJECTS_DETECTION").last()
            obj, created = Subscriptions.objects.get_or_create(user=request.user, plan=plan)
            obj.requests_send += 1
            obj.save()
            if obj.requests_send >= obj.plan.requests:
                obj.is_expired = True
                obj.save()
        if request.user.premium == 0:
            plan = Plans.objects.filter(access="OBJECTS_DETECTION").last()
            obj, create = FreeSubscriptions.objects.get_or_create(user=request.user, plan=plan)
            obj.requests_send += 1
            obj.save()
            if obj.requests_send >= obj.plan.free_requests:
                obj.is_expired = True
                obj.save()
    except Exception as e:
        pass
    return JsonResponse(data, safe=False)


def CreateAPIkey(request):
    Token.objects.filter(user=request.user).delete()
    token = Token.objects.create(user=request.user)
    return HttpResponse(str(token.key))


def DeleteAPIkey(request):
    Token.objects.filter(user=request.user).delete()
    return HttpResponse("")


def ApiKeyView(request):
    try:
        token = Token.objects.get(user=request.user).key
        return render(request, "apikey.html", {"token": token})
    except Exception as e:
        return render(request, "apikey.html")


def OurPlans(request):
    context = {
        "monthly_plans": Plans.objects.filter(plan_type="MONTHLY").order_by("-added_on"),
        "yearly_plans":  Plans.objects.filter(plan_type="YEARLY"),
        "time_period_plans": Plans.objects.filter(plan_type="TIMEPERIOD"),
    }
    return render(request, "plans.html", context=context)


def IndustriesView(request):
    industries = Industries.objects.all().order_by("added_on")
    p = Paginator(industries, 1)  # creating a paginator object
    # getting the desired page number from url
    page_number = request.GET.get('page')
    try:
        page_obj = p.get_page(page_number)  # returns the desired page object
    except PageNotAnInteger:
        # if page_number is not an integer then assign the first page
        page_obj = p.page(1)
    except EmptyPage:
        # if page is empty then return last page
        page_obj = p.page(p.num_pages)
    context = {'page_obj': page_obj}
    # sending the page object to index.html
    return render(request, "industries.html", context=context)


def JobsView(request):
    industries = Jobs.objects.all().order_by("added_on")
    p = Paginator(industries, 1)  # creating a paginator object
    # getting the desired page number from url
    page_number = request.GET.get('page')
    try:
        page_obj = p.get_page(page_number)  # returns the desired page object
    except PageNotAnInteger:
        # if page_number is not an integer then assign the first page
        page_obj = p.page(1)
    except EmptyPage:
        # if page is empty then return last page
        page_obj = p.page(p.num_pages)
    context = {'page_obj': page_obj}
    # sending the page object to index.html
    return render(request, "jobs.html", context=context)


def CapabilitiesView(request):
    industries = Capabilities.objects.all().order_by("added_on")
    p = Paginator(industries, 1)  # creating a paginator object
    # getting the desired page number from url
    page_number = request.GET.get('page')
    try:
        page_obj = p.get_page(page_number)  # returns the desired page object
    except PageNotAnInteger:
        # if page_number is not an integer then assign the first page
        page_obj = p.page(1)
    except EmptyPage:
        # if page is empty then return last page
        page_obj = p.page(p.num_pages)
    context = {'page_obj': page_obj}
    # sending the page object to index.html
    return render(request, "capabilities.html", context=context)


def GetIndustriesData(request):
    industries = list(Industries.objects.all().values("title", "slogan"))
    return JsonResponse(industries, safe=False)


def Communities(request):
    q = request.POST.get("q")
    if q:
        communities = Community.objects.filter(name__icontains=q)
    else:
        communities = Community.objects.all()

    page_num = request.GET.get('page', 1)

    paginator = Paginator(communities.order_by("-added_on"), 8)
    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        # if page is not an integer, deliver the first page
        page_obj = paginator.page(1)
    except EmptyPage:
        # if the page is out of range, deliver the last page
        page_obj = paginator.page(paginator.num_pages)

    return render(request, "communities.html", context={
        "communities": communities,
        "page_obj": page_obj
    })


def CreateTeams(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            team_name = request.POST.get("team_name")
            logo = request.FILES.get("logo")
            community = Community.objects.create(name=team_name, logo=logo, leader=request.user)
            CommunityMembers.objects.create(user=request.user, community=community)
        return render(request, "create_teams.html")
    return redirect("/api/login/")


def JoinedCommunities(request):
    if request.user.is_authenticated:
        if CommunityMembers.objects.filter(user=request.user).exists():
            communities_id = request.user.team.all().values_list("community__community_id", flat=True)
            communities = Community.objects.filter(community_id__in=communities_id)
            return render(request, "joined_communities.html", context={"communities": communities})
        return render(request, "joined_communities.html")
    return redirect("/api/login/")


def JoinCommunity(request):
    try:
        if request.user.is_authenticated:
            uri = request.build_absolute_uri('/')
            is_leader = False
            members = list()
            show_welcome_ms = request.POST.get("show_welcome_ms", None)
            try:
                team_id = request.POST.get("team_id", None)
                community = Community.objects.get(community_id=team_id)
            except Exception as e:
                team_id = request.GET.get("team_id")
                community = Community.objects.get(community_id=team_id)
            member, created = CommunityMembers.objects.get_or_create(user=request.user, community=community)
            if request.user.community_leaders.filter(community_id=community.community_id).exists():
                is_leader = True
            for com in community.members.all():
                members.append(dict({
                    "f_name": com.user.first_name,
                    "l_name": com.user.last_name,
                    "email": com.user.email
                }))
            posts = community.feed.all().order_by("-added_on")
            page_num = request.GET.get('page', 1)
            paginator = Paginator(posts, 4)
            try:
                page_obj = paginator.page(page_num)
            except PageNotAnInteger:
                # if page is not an integer, deliver the first page
                page_obj = paginator.page(1)
            except EmptyPage:
                # if the page is out of range, deliver the last page
                page_obj = paginator.page(paginator.num_pages)
            context = {
                "keywords": community.keywords.all(),
                "community": community,
                "total_members": community.members.all().count(),
                "page_obj": page_obj,
                "members": members,
                "is_leader": is_leader,
                "uri": uri,
                "team_id": community.community_id,
                "categories": Category.objects.all(),
            }
            if not created:
                return render(request, "community_responses.html", context=context)
            if show_welcome_ms:
                messages.success(request, "Congratulations you have joined team successfully")
            return render(request, "community_responses.html", context=context)
        return redirect("/api/login/")
    except Community.DoesNotExist:
        return redirect("/communities/")


def SendPostCommunity(request):
    page = request.POST.get("page")
    try:
        # question = request.GET.get('question', '')
        # response = request.GET.get('response', '')
        # images = request.GET.get('images', None)
        question = request.POST.get("input")
        response = request.POST.get("response")
        images = request.POST.get("images")
        multiple_communities = request.POST.getlist("multiple_communities")
        multiple_communities = [int(item) for item in multiple_communities]
        all_comms = CommunityMembers.objects.filter(user=request.user, community__id__in=multiple_communities)
        if images:
            images = images.split(",")
            for comm in all_comms:
                post = CommunityPosts.objects.create(
                    user=request.user, community=comm.community, question=question)
                post.image1 = images[0]
                post.image2 = images[2]
                post.image3 = images[2]
                post.save()
        else:
            for comm in all_comms:
                send = True
                keywords = list(comm.community.keywords.all().values_list("keyword", flat=True))
                keywords = [x.upper() for x in keywords]
                input_keywords = question.split(" ")
                for key in input_keywords:
                    if key.upper() in keywords:
                        send = False
                if send:
                    CommunityPosts.objects.create(
                        user=request.user, community=comm.community, question=question, response=response)
        if page == "text_to_text":
            return redirect("/api/text_to_text/")
        elif page == "retail_bots":
            return redirect("/api/retail_bots/")
        else:
            return redirect("/api/text_to_image/")
    except CommunityMembers.DoesNotExist:
        if page == "text_to_text":
            return redirect("/api/text_to_text/")
        else:
            return redirect("/api/text_to_text/")


def SendObjectCommunity(request):
    page = request.POST.get("page")
    image_input = request.POST.get("image_input")
    image_response = request.POST.get("image_response")
    multiple_communities = request.POST.getlist("multiple_communities")
    multiple_communities = [int(item) for item in multiple_communities]
    all_comms = CommunityMembers.objects.filter(user=request.user, community__id__in=multiple_communities)
    for comm in all_comms:
        CommunityPosts.objects.create(
            user=request.user, community=comm.community, input_image=image_input, response_image=image_response)

    return redirect("/api/image/objects/detection/")


def UploadCommunityPost(request):
    team_id = request.POST.get("team_id")
    name = request.POST.get("item_name")
    cat = request.POST.get("item_category")
    image = request.FILES.get("item_image")
    item_image_url = request.POST.get("item_image_url", None)
    video = request.FILES.get("item_video", None)
    item_desc = request.POST.get("item_desc")
    upload = request.POST.get("upload")
    question = "How to use {}".format(name)
    if item_image_url:
        print(item_image_url)
        response1 = urlopen(item_image_url)
        image = BytesIO(response1.read())
        # imagedb.image1.save("image_one.jpg", File(io1))
    com = Community.objects.get(community_id=team_id)
    post = CommunityPosts.objects.create(user=request.user, question=question, response=item_desc, community=com)
    if upload == "yes":
        category, created = Category.objects.get_or_create(title=cat)
        if video:
            item = Items.objects.create(
                category=category, title=name, description=item_desc, video=video)
        else:
            item = Items.objects.create(
                category=category, title=name, description=item_desc)
        result = urllib.request.urlretrieve(item.qr_code.url)
        if video:
            result2 = urllib.request.urlretrieve(item.video.url)
        with open(result[0], 'rb') as f:
            # Set the image field to the downloaded file
            post.qrcode.save("test.png", File(f))
        if video:
            with open(result2[0], 'rb') as fa:
                # Set the image field to the downloaded file
                post.video.save("test.mp4", File(fa))
        item.image.save("image_one.jpg", File(image))
        if item_image_url:
            result = urllib.request.urlretrieve(item_image_url)
            with open(result[0], 'rb') as G:
                # Set the image field to the downloaded file
                post.image.save("test.png", File(G))
        post.item_name = item.title
        post.save()
    return redirect("/join/community/?team_id={}".format(team_id))


def Checkout(request, plan_id):
    plan = Plans.objects.get(id=plan_id)
    return render(request, "checkout.html", context={"plan": plan})


def PaymentSuccess(request, plan_id, user_id):
    plan = Plans.objects.get(id=plan_id)
    user = User.objects.get(id=user_id)
    user.access = plan.access
    user.premium = 1
    user.purchased_on = timezone.now()
    user.save()
    Subscriptions.objects.create(user=user, plan=plan)
    return render(request, "payment_success.html", context={"plan": plan})


def ItemPaymentSuccess(request, item_id, user_id):
    return HttpResponse("Item Purchased Successfully")



def PaymentCancel(request):
    return HttpResponse("PAYMENT CANCEL")


def ValidateCouponCode(request, coupon_code):
    try:
        coupon = CouponCode.objects.get(code=coupon_code.split("=")[1], is_expired=False)
        coupon.is_expired = True
        coupon.save()
        return JsonResponse(["valid", coupon.price], safe=False)
    except Exception as e:
        return JsonResponse(["invalid"], safe=False)


def ShareTeam(request, team_id):
    members = list()
    team = Community.objects.get(id=team_id)
    for com in team.members.all():
        members.append(dict({
            "first_name": com.user.first_name,
            "last_name": com.user.last_name,
            "email": com.user.email,
        }))
    return render(request, "shareteam.html", context={
        "team": team,
        "members": members,
        "total_members": len(members)
    })


def DownloadTeams(request):
    uri = request.build_absolute_uri('/')
    communities = list()
    for community in Community.objects.all():
        communities.append({
            "name": community.name,
            "community_id": community.community_id,
            "link": uri + "team/share/{}/".format(community.id)
        })
    dataframe = pd.DataFrame(communities, index=None)
    excel_file = IO()
    xl_writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
    dataframe.to_excel(xl_writer, 'ActiveLicenses', index=False)
    xl_writer.save()
    excel_file.seek(0)
    response = HttpResponse(excel_file.read(), content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=all_team.xlsx'
    return response


def ShopWithText(request):
    q = request.POST.get("q")
    if q:
        items = Items.objects.filter(title__icontains=q)
    else:
        items = []
    return render(request, "text_shop.html", context={"items": items})


def ShopCheckout(request, item_id):
    item = Items.objects.get(pk=int(item_id))
    return render(request, "shop_checkout.html", {"item": item})



def ItemHowToUse(request, item_id):
    item = Items.objects.get(id=item_id)
    if request.method == "POST":
        uses = request.POST.get("usecase")
        item.description = uses
        item.save()
    return render(request, "item_uses.html", context={"item": item})


def LearHowToUse(request, item_id):
    item = Items.objects.get(id=item_id)
    return render(request, "item_detail.html", context={"item": item})


def KeyManagementView(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            key = request.POST.get("key")
            organization = request.POST.get("organization")
            KeyManagement.objects.get_or_create(user=request.user, key=key, organization=organization, platform="OPENAI")
        keys = request.user.keys.filter(platform="OPENAI")
        return render(request, "key_management.html", {"keys": keys})
    return redirect("/api/login/")


def MicrosoftKeyManagementView(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            key = request.POST.get("key")
            endpoint = request.POST.get("endpoint")
            organization = request.POST.get("organization")
            KeyManagement.objects.get_or_create(
                user=request.user, key=key, organization=organization, platform="MICROSOFT", endpoint=endpoint)
        keys = request.user.keys.filter(platform="MICROSOFT")
        return render(request, "ms_key_management.html", context={'keys': keys})
    return redirect("/api/login/")


def ForgotPassword(request):
    try:
        if request.method == "POST":
            email = request.POST.get("email")
            user = User.objects.get(email=email)
            token = random.randint(10000, 99999)
            user.reset_token = token
            user.save()
            subject = 'Password Reset Token'
            message = 'Your password reset token is {}'.format(token)
            user.email_user(subject, message, from_email="no-reply@doctustech.com")
            return redirect("/api/change/password/")
        return render(request, "forgot_password.html")
    except User.DoesNotExist:
        return redirect("/api/forgot/password/")


def ChangePassword(request):
    try:
        if request.method == "POST":
            token = request.POST.get("token")
            password = request.POST.get("password")
            user = User.objects.get(reset_token=token)
            user.set_password(password)
            user.save()
            return redirect("/api/login/")
        return render(request, "change_password.html")
    except User.DoesNotExist:
        return redirect("/api/change/password/")


def RenewSubscription(request):
    return render(request, "renew.html")


def deletekey(request, id):
    ms = request.GET.get("MS", None)
    KeyManagement.objects.filter(id=id).delete()
    if ms:
        return redirect("/api/microsoft/keys/")
    return redirect("/api/key/management/")


def WatchVideo(request, item_id):
    item = Items.objects.get(item_id=item_id)
    return render(request, "video.html", context={"item": item})


def TextToTextDetail(request):
    has_expired = False
    plan = Plans.objects.filter(access="TEXT_TO_TEXT").last()
    if request.user.is_authenticated:
        if plan:
            if request.user.free_purchases.filter(plan=plan).exists():
                plan_sub = request.user.free_purchases.filter(plan=plan).last()
                if int(plan_sub.requests_send) >= int(plan.free_requests):
                    has_expired = True
    return render(request, "text2textdetail.html", context={"plan": plan, "has_expired": has_expired})


def VoiceToVoiceDetail(request):
    has_expired = False
    plan = Plans.objects.filter(access="VOICE_TO_Voice").last()
    if request.user.is_authenticated:
        if plan:
            if request.user.free_purchases.filter(plan=plan).exists():
                plan_sub = request.user.free_purchases.filter(plan=plan).last()
                if int(plan_sub.requests_send) >= int(plan.free_requests):
                    has_expired = True
    return render(request, "voice2voicedetail.html", context={"plan": plan, "has_expired": has_expired})


def VoiceToImageDetail(request):
    has_expired = False
    plan = Plans.objects.filter(access="VOICE_TO_IMAGE").last()
    if request.user.is_authenticated:
        if plan:
            if request.user.free_purchases.filter(plan=plan).exists():
                plan_sub = request.user.free_purchases.filter(plan=plan).last()
                if int(plan_sub.requests_send) >= int(plan.free_requests):
                    has_expired = True
    return render(request, "voice2imagedetail.html", context={"plan": plan, "has_expired": has_expired})


def TextToVoiceDetail(request):
    has_expired = False
    plan = Plans.objects.filter(access="TEXT_TO_VOICE").last()
    if request.user.is_authenticated:
        if plan:
            if request.user.free_purchases.filter(plan=plan).exists():
                plan_sub = request.user.free_purchases.filter(plan=plan).last()
                if int(plan_sub.requests_send) >= int(plan.free_requests):
                    has_expired = True
    return render(request, "text2voicedetail.html", context={
        "plan": plan, "has_expired": has_expired})


def TextToImageDetail(request):
    has_expired = False
    plan = Plans.objects.filter(access="TEXT_TO_IMAGE").last()
    if request.user.is_authenticated:
        if plan:
            if request.user.free_purchases.filter(plan=plan).exists():
                plan_sub = request.user.free_purchases.filter(plan=plan).last()
                if int(plan_sub.requests_send) >= int(plan.free_requests):
                    has_expired = True
    return render(request, "text2imagedetail.html", context={
        "plan": plan, "has_expired": has_expired})


def ImageToImageDetail(request):
    has_expired = False
    plan = Plans.objects.filter(access="IMAGE_TO_IMAGE").last()
    if request.user.is_authenticated:
        if plan:
            if request.user.free_purchases.filter(plan=plan).exists():
                plan_sub = request.user.free_purchases.filter(plan=plan).last()
                if int(plan_sub.requests_send) >= int(plan.free_requests):
                    has_expired = True
    return render(request, "image2imagedetail.html", context={
        "plan": plan, "has_expired": has_expired})


def ImageAnalysisDetail(request):
    has_expired = False
    plan = Plans.objects.filter(access="IMAGE_ANALYSIS").last()
    if request.user.is_authenticated:
        if plan:
            if request.user.free_purchases.filter(plan=plan).exists():
                plan_sub = request.user.free_purchases.filter(plan=plan).last()
                if int(plan_sub.requests_send) >= int(plan.free_requests):
                    has_expired = True
    return render(request, "imageanalysisdetail.html", context={
        "plan": plan, "has_expired": has_expired})


def ImageDetectDetail(request):
    has_expired = False
    plan = Plans.objects.filter(access="OBJECTS_DETECTION").last()
    if request.user.is_authenticated:
        if plan:
            if request.user.free_purchases.filter(plan=plan).exists():
                plan_sub = request.user.free_purchases.filter(plan=plan).last()
                if int(plan_sub.requests_send) >= int(plan.free_requests):
                    has_expired = True
    return render(request, "imagedetectdetail.html", context={
        "plan": plan, "has_expired": has_expired})


def VoiceToCommandDetail(request):
    has_expired = False
    plan = Plans.objects.filter(access="VOICE_TO_COMMAND").last()
    if request.user.is_authenticated:
        if plan:
            if request.user.free_purchases.filter(plan=plan).exists():
                plan_sub = request.user.free_purchases.filter(plan=plan).last()
                if int(plan_sub.requests_send) >= int(plan.free_requests):
                    has_expired = True
    return render(request, "voice2commanddetail.html", context={
        "plan": plan, "has_expired": has_expired})


def TextToCommandDetail(request):
    has_expired = False
    plan = Plans.objects.filter(access="TEXT_TO_COMMAND").last()
    if request.user.is_authenticated:
        if plan:
            if request.user.free_purchases.filter(plan=plan).exists():
                plan_sub = request.user.free_purchases.filter(plan=plan).last()
                if int(plan_sub.requests_send) >= int(plan.free_requests):
                    has_expired = True
    return render(request, "text2commanddetail.html", context={
        "plan": plan, "has_expired": has_expired})


def ImageToTextDetail(request):
    has_expired = False
    plan = Plans.objects.filter(access="Image_To_Text").last()
    if request.user.is_authenticated:
        if plan:
            if request.user.free_purchases.filter(plan=plan).exists():
                plan_sub = request.user.free_purchases.filter(plan=plan).last()
                if int(plan_sub.requests_send) >= int(plan.free_requests):
                    has_expired = True
    return render(request, "image2textdetail.html", context={
        "plan": plan, "has_expired": has_expired})


@csrf_exempt
def SaveCapturedPhoto(request):
    photo_data = request.POST.get("photo")
    image_data = base64.b64decode(photo_data.split(',')[1])

    # Create an in-memory file-like object
    image_file = BytesIO(image_data)

    # Create an Image object from the file
    image = Image.open(image_file)

    # Create an InMemoryUploadedFile object to save to the database
    image_file = InMemoryUploadedFile(
        image_file,  # file-like object
        None,  # field name (unused)
        'photo.jpg',  # file name
        'image/jpeg',  # content type
        image.size,  # size
        None  # charset (unused)
    )
    img = CapturedImages.objects.create(image=image_file)
    return HttpResponse(str(img.image.url))


@csrf_exempt
def ImageAnalysisOCR(request):
    photo_data = request.POST.get("image_data")
    image_data = base64.b64decode(photo_data.split(',')[1])

    # Create an in-memory file-like object
    image_file = BytesIO(image_data)

    # Create an Image object from the file
    image = Image.open(image_file)

    # Create an InMemoryUploadedFile object to save to the database
    image_file = InMemoryUploadedFile(
        image_file,  # file-like object
        None,  # field name (unused)
        'photo.jpg',  # file name
        'image/jpeg',  # content type
        image.size,  # size
        None  # charset (unused)
    )
    img = CapturedImages.objects.create(image=image_file)
    subscription_key = "B0faa09900954b4ab9eee55e133399cc"
    endpoint = "https://bennyocr.cognitiveservices.azure.com/"
    computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
    read_response = computervision_client.read(str(img.image.url), raw=True)
    # Get the operation location (URL with an ID at the end) from the response
    read_operation_location = read_response.headers["Operation-Location"]
    # Grab the ID from the URL
    operation_id = read_operation_location.split("/")[-1]

    # Call the "GET" API and wait for it to retrieve the results
    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)
    response = ""
    # Print the detected text, line by line
    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                response += line.text + "\n"
    return HttpResponse(str(response))


def RedirectPlan(request, plan_id):
    plan = Plans.objects.get(id=plan_id)
    if plan.access == "VOICE_TO_Voice":
        return reverse("voice2voicePlanDetail")


def voice2voicePlanDetail(request):
    plan = Plans.objects.get(access="VOICE_TO_Voice")
    return render(request, "plans/voice2voicedetail.html", context={"plan": plan})


def voice2ImagePlanDetail(request):
    plan = Plans.objects.get(access="VOICE_TO_IMAGE")
    return render(request, "plans/voice2ImagePlanDetail.html", context={"plan": plan})


def text2VoicePlanDetail(request):
    plan = Plans.objects.get(access="TEXT_TO_VOICE")
    return render(request, "plans/text2VoicePlanDetail.html", context={"plan": plan})


def text2TextPlanDetail(request):
    plan = Plans.objects.get(access="TEXT_TO_TEXT")
    return render(request, "plans/text2TextPlanDetail.html", context={"plan": plan})


def text2ImagePlanDetail(request):
    plan = Plans.objects.get(access="TEXT_TO_IMAGE")
    return render(request, "plans/text2ImagePlanDetail.html", context={"plan": plan})


def image2ImagePlanDetail(request):
    plan = Plans.objects.get(access="IMAGE_TO_IMAGE")
    return render(request, "plans/image2ImagePlanDetail.html", context={"plan": plan})


def object_detectPlanDetail(request):
    plan = Plans.objects.get(access="OBJECTS_DETECTION")
    return render(request, "plans/object_detectPlanDetail.html", context={"plan": plan})


def voice2commandPlanDetail(request):
    plan = Plans.objects.get(access="VOICE_TO_COMMAND")
    return render(request, "plans/voice2commandPlanDetail.html", context={"plan": plan})


def text2commandPlanDetail(request):
    plan = Plans.objects.get(access="TEXT_TO_COMMAND")
    return render(request, "plans/text2commandPlanDetail.html", context={"plan": plan})


def OcrPlanDetail(request):
    plan = Plans.objects.get(access="Image_To_Text")
    return render(request, "plans/OcrPlanDetail.html", context={"plan": plan})


def imageAnalysisPlanDetail(request):
    plan = Plans.objects.get(access="IMAGE_ANALYSIS")
    return render(request, "plans/imageAnalysisPlanDetail.html", context={"plan": plan})


def RetailBotsView(request):
    communities = []
    if CommunityMembers.objects.filter(user=request.user).exists():
        communities_id = request.user.team.all().values_list("community__community_id", flat=True)
        communities = Community.objects.filter(community_id__in=communities_id)
    return render(request, "retail_bots.html", {"communities": communities})



