from django.contrib.auth import authenticate, login
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
import speech_recognition as sr
import openai
from django.views.decorators.csrf import csrf_exempt
from users.models import User


openai.api_key = ""


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


def VoiceToVoice(request):
    return render(request, "voice_to_voice.html")

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
    no_of_images = request.GET.get('no_of_images', 2)
    response = openai.Image.create(prompt="{}".format(text), n=int(no_of_images), size="1024x1024")
    images = list()
    for image in response['data']:
        images.append(image.url)
    return JsonResponse(images, safe=False)


def get_chatgpt_response(request):
    prompt = request.GET.get('text', '')
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
