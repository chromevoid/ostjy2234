# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404, redirect

from django.http import HttpResponse

from .models import *
from django.contrib import messages

from google.appengine.api import users

import datetime
import random
import re


# Create your views here.


def index(request):
    return render(request, 'landing.html')


def new(request):
    return render(request, 'new.html')


def resource(request):
    return render(request, 'recourse.html')


def create_resource(request):
    new_resource = Resource()
    new_resource.created = datetime.datetime.now()
    new_resource.owner = users.get_current_user()
    new_resource.name = request.POST['name']
    new_resource.start = request.POST['start']
    new_resource.end = request.POST['end']
    new_resource.tags = request.POST['tags']
    new_resource.description = request.POST['description']
    new_resource.save()
    return redirect(request.META.get('HTTP_REFERER'))
