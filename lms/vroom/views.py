from multiprocessing import context
from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .models import *


def index(request):
    return render(request, 'vroom/index.html')

@login_required
def entrega(request):
    return render(request, 'vroom/entrega.html')

@login_required
def dashboard(request):
    return render(request, 'vroom/dashboard.html')
