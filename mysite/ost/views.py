# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse


def index(request):
    return render(request, 'landing.html')


def new(request):
    return render(request, 'new.html')


def resource(request):
    return render(request, 'recourse.html')

