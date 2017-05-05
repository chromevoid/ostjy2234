# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404, redirect

from django.http import HttpResponse

from .models import *
from django.contrib import messages

from google.appengine.api import users

import datetime


# Create your views here.


def index(request):
    my_reservation_list = Reservation.objects.filter(
        owner=users.get_current_user(),
    )
    resource_list = Resource.objects.all()
    tag_lists = []
    for r in resource_list:
        tag_lists.append(r.tags.all())
    my_resource_list = Resource.objects.filter(
        owner=users.get_current_user(),
    )
    my_tag_lists = []
    for r in my_resource_list:
        my_tag_lists.append(r.tags.all())
    return render(request, 'landing.html', {
        'my_reservation_list': my_reservation_list,
        'resource_list': resource_list,
        'tag_lists': tag_lists,
        'my_resource_list': my_resource_list,
        'my_tag_lists': my_tag_lists,
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
    new_resource.description = request.POST['description']
    new_resource.last = datetime.datetime.now()
    new_resource.save()
    tags = request.POST['tags'].split(",")
    for tag in tags:
        old_tag = Tag.objects.filter(name=tag)
        if len(old_tag) == 0:
            new_tag = Tag()
            new_tag.name = tag
            new_tag.save()
            new_resource.tags.add(new_tag)
        else:
            new_resource.tags.add(Tag.objects.filter(name=tag)[:1].get())
    return redirect(request.META.get('HTTP_REFERER'))


def update_resource(request, resource_id=None):
    current_resource = get_object_or_404(Resource, pk=resource_id)
    current_resource.name = request.POST['name']
    current_resource.start = request.POST['start']
    current_resource.end = request.POST['end']
    current_resource.description = request.POST['description']
    current_resource.save()
    current_resource.tags.clear()
    tags = request.POST['tags'].split(",")
    for tag in tags:
        old_tag = Tag.objects.filter(name=tag)
        if len(old_tag) == 0:
            new_tag = Tag()
            new_tag.name = tag
            new_tag.save()
            current_resource.tags.add(new_tag)
        else:
            current_resource.tags.add(Tag.objects.filter(name=tag)[:1].get())
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
