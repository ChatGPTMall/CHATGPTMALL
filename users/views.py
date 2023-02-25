from django.shortcuts import render


def HomepageView(request):
    return render(request, "homepage.html")