from django.shortcuts import render

def home(request):
    return render(request, 'vaultapp/home.html')

def about(request):
    return render(request,'vaultapp/about.html')