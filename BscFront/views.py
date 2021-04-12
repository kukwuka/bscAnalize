from django.shortcuts import render


# Create your views here.

def index_html(request):
    return render(request, 'main.html')
