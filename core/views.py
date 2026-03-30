from django.shortcuts import render

def landing(request):
    return render(request, 'landing.html')

def login_page(request):
    return render(request, 'login.html')