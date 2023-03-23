import os
import urllib
from io import BytesIO
from urllib import request
from urllib.request import urlopen

import openai
from django.core.files import File
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from users.models import User
import speech_recognition as sr
from django.db import IntegrityError
from django.shortcuts import render, redirect
from rest_framework.authtoken.models import Token
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from engine.models import ResponsesDB, VoiceToVoiceRequests, ImagesDB, ShopAccess, Plans, Industries, Capabilities, \
    Jobs, Community, CommunityMembers, CommunityPosts, CouponCode, Subscriptions

openai.api_key = os.getenv("OPEN_AI_KEY")


def HomepageView(request):
    show_logo = False
    DEPLOYED_HOST = os.getenv("DEPLOYED_HOST", None)
    if DEPLOYED_HOST == "https://madeinthai.org":
        show_logo = True
    return render(request, "homepage.html", context={"show_logo": show_logo})


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
                Token.objects.get_or_create(user=user)
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
    if request.user.is_authenticated:
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
    URL = os.getenv("DEPLOYED_HOST", "https://my.chatgptmall.tech")
    if not response:
        response = openai.Image.create(prompt="{}".format(text), n=3, size="1024x1024")
        images = list()
        for image in response['data']:
            images.append(image.url)
        if request.user.is_authenticated:
            imagedb = ImagesDB.objects.create(question=text, user=request.user)
        else:
            ImagesDB.objects.create(question=text, images=images)

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

        return JsonResponse(show_images, safe=False)
    else:
        show_images = list()
        show_images.append(URL+response.last().image1.url)
        show_images.append(URL+response.last().image2.url)
        show_images.append(URL+response.last().image3.url)
        return JsonResponse(show_images, safe=False)


def GetImages(request):
    pass


def get_chatgpt_response(request):
    try:
        obj = VoiceToVoiceRequests.objects.get(user=request.user)
        obj.requests_send += 1
        obj.save()
    except Exception as e:
        VoiceToVoiceRequests.objects.create(user=request.user, requests_send=1)
    prompt = request.GET.get('text', '')
    words = request.GET.get('words')
    response = ResponsesDB.objects.filter(question__icontains=prompt)
    if not response:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            max_tokens=int(words),
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


def TextToImage(request):
    return render(request, "TextToImage.html")


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
        "monthly_plans": Plans.objects.filter(plan_type="MONTHLY"),
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
    is_member = False
    if request.user.is_authenticated:
        if CommunityMembers.objects.filter(user=request.user).exists():
            is_member = True
            communities = Community.objects.filter(community_id=request.user.team.community.community_id)
        else:
            communities = Community.objects.all()
    else:
        communities = Community.objects.all()
    return render(request, "communities.html", context={
        "communities": communities,
        "is_member": is_member,
    })


def JoinCommunity(request):
    try:
        if request.user.is_authenticated:

            team_id = request.POST.get("team_id", None)
            show_welcome_ms = request.POST.get("show_welcome_ms", None)
            community = Community.objects.get(community_id=team_id)
            member, created = CommunityMembers.objects.get_or_create(user=request.user, community=community)
            context = {
                "community": community,
                "total_members": community.members.all().count(),
                "posts": community.feed.all()
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
    try:
        question = request.GET.get('question', '')
        response = request.GET.get('response', '')
        if not CommunityPosts.objects.filter(question=question).exists():
            community = CommunityMembers.objects.get(user=request.user)
            CommunityPosts.objects.create(
                user=request.user, community=community.community, question=question, response=response)
            return HttpResponse("Post Uploaded Successfully")
        return HttpResponse("Post Already Exists")
    except CommunityMembers.DoesNotExist:
        return HttpResponse("Community Does Not Exist For You")


def Checkout(request, plan_id):
    plan = Plans.objects.get(id=plan_id)
    return render(request, "checkout.html", context={"plan": plan})


def PaymentSuccess(request, plan_id, user_id):
    plan = Plans.objects.get(id=plan_id)
    user = User.objects.get(id=user_id)
    user.access = plan.access
    user.save()
    Subscriptions.objects.create(user=user, plan=plan)
    return render(request, "payment_success.html", context={"plan": plan})


def PaymentCancel(request):
    return HttpResponse("PAYMENT CANCEL")


def ValidateCouponCode(request, coupon_code):
    try:
        coupon = CouponCode.objects.get(code=coupon_code.split("=")[1])

        return JsonResponse(["valid", coupon.price], safe=False)
    except Exception as e:
        print(e)
        return JsonResponse(["invalid"], safe=False)


