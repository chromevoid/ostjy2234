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
    my_reservation_list = Reservation.objects.filter(
        owner=users.get_current_user(),
    )
    resource_list = Resource.objects.all()
    my_resource_list = Resource.objects.filter(
        owner=users.get_current_user(),
    )
    return render(request, 'landing.html', {
        'my_reservation_list': my_reservation_list,
        'resource_list': resource_list,
        'my_resource_list': my_resource_list,
    })


def new(request):
    return render(request, 'new.html')


def resource(request, resource_id=None):
    current_resource = get_object_or_404(Resource, pk=resource_id)
    my_resource = Resource.objects.filter(
        owner=users.get_current_user(),
        pk=resource_id,
    )
    edit = False
    if len(my_resource) != 0:
        edit = True
    reservation_list = Reservation.objects.filter(
        resource=current_resource,
    )
    return render(request, 'resource.html', {
        'current_resource': current_resource,
        'current_user': users.get_current_user(),
        'edit': edit,
        'reservation_list': reservation_list,
    })


def create_resource(request):
    new_resource = Resource()
    new_resource.created = datetime.datetime.now()
    new_resource.owner = users.get_current_user()
    new_resource.name = request.POST['name']
    new_resource.start = request.POST['start']
    new_resource.end = request.POST['end']
    new_resource.tags = request.POST['tags']
    new_resource.description = request.POST['description']
    new_resource.last = datetime.datetime.now()
    new_resource.save()
    return redirect(request.META.get('HTTP_REFERER'))


def update_resource(request, resource_id=None):
    current_resource = get_object_or_404(Resource, pk=resource_id)
    current_resource.name = request.POST['name']
    current_resource.start = request.POST['start']
    current_resource.end = request.POST['end']
    current_resource.tags = request.POST['tags']
    current_resource.description = request.POST['description']
    current_resource.save()
    return redirect(request.META.get('HTTP_REFERER'))


def create_reservation(request, resource_id=None):
    current_resource = get_object_or_404(Resource, pk=resource_id)
    new_reservation = Reservation()
    new_reservation.created = datetime.datetime.now()
    new_reservation.owner = users.get_current_user()
    new_reservation.resource = current_resource
    new_reservation.time = request.POST['time']
    new_reservation.duration = request.POST['duration']

    new_reservation_time, minute_reservation = request.POST['time'].split(":")
    current_resource_end, minute_resource = current_resource.end.split(":")
    if int(new_reservation_time) + int(request.POST['duration']) > int(current_resource_end):
        messages.error(request, "Time not available")
    else:
        new_reservation.save()
        current_resource.last = datetime.datetime.now()
        current_resource.save()
    return redirect(request.META.get('HTTP_REFERER'))


def delete_reservation(request, reservation_id=None):
    current_reservation = get_object_or_404(Reservation, pk=reservation_id)
    current_reservation.delete()
    return redirect(request.META.get('HTTP_REFERER'))
