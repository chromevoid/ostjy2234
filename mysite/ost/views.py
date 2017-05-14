# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import *
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.syndication.views import Feed
from google.appengine.api import users
from google.appengine.api import mail

import datetime


# Create your views here.


def index(request, name_results=[], time_results=[]):
    # get the reservations made by the current user
    my_reservation_list = Reservation.objects.filter(
        owner=users.get_current_user(),
    ).order_by('time')

    # get the resources in the system
    resource_list = Resource.objects.all().order_by('-last')

    # get the resources owned by the current user
    my_resource_list = Resource.objects.filter(
        owner=users.get_current_user(),
    )
    # to order the time correctly and ignore reservations that pass the time
    current = (datetime.datetime.now() + datetime.timedelta(hours=-4)).strftime('%H:%M')
    current_hour, current_minute = current.split(":")
    current_time_in_minutes = int(current_hour) * 60 + int(current_minute)
    am_helper_list = []
    pm_helper_list = []
    for reservation in my_reservation_list:
        time, sign = reservation.time.split(" ")
        hour, minute = time.split(":")
        if sign == "AM":
            hour = int(hour) if int(hour) != 12 else 0
            end = hour * 60 + int(minute) + int(reservation.duration) * 60
            if current_time_in_minutes <= end:
                am_helper_list.append(reservation)
        else:
            hour = int(hour) + 12
            end = hour * 60 + int(minute) + int(reservation.duration) * 60
            if current_time_in_minutes <= end:
                pm_helper_list.append(reservation)

    return render(request, 'landing.html', {
        'my_reservation_list': my_reservation_list,
        'resource_list': resource_list,
        'my_resource_list': my_resource_list,
        'hour': current_hour,
        'minute': current_minute,
        'am_helper_list': am_helper_list,
        'pm_helper_list': pm_helper_list,
        'name_results': name_results,
        'time_results': time_results,
    })


def search_by_name(request):
    # get the search name
    name = request.POST['search_by_name'].lower()

    # get the resources in the system
    resource_list = Resource.objects.all().order_by('-last')

    # check the name of each resource
    # if the search name is a substring of the resource name, then add the resource to the result_list
    show_resource_list = []
    for r in resource_list:
        if r.name.lower().find(name) >= 0:
            show_resource_list.append(r)

    return index(request, show_resource_list, [])


def search_by_time(request):
    # get the fields, and convert HH:MM AM/PM to minutes
    search_duration = request.POST['duration']
    search_time, search_sign = request.POST['time'].split(" ")
    search_hour, search_minute = search_time.split(":")
    if search_sign == "AM":
        search_hour = int(search_hour) if int(search_hour) != 12 else 0
    else:
        search_hour = int(search_hour) + 12
    search_start = search_hour * 60 + int(search_minute)
    search_end = search_start + int(search_duration) * 60

    # get the resources in the system
    resource_list = Resource.objects.all().order_by('-last')

    # check if the the start time and end time of a resource is within the search time period
    # if true, then add the resource to the result_list
    resource_list_avaible = []
    for r in resource_list:
        time_start, sign_start = r.start.split(" ")
        hour_start, minute_start = time_start.split(":")
        time_end, sign_end = r.end.split(" ")
        hour_end, minute_end = time_end.split(":")
        if sign_start == "AM":
            hour_start = int(hour_start) if int(hour_start) != 12 else 0
        else:
            hour_start = int(hour_start) + 12
        if sign_end == "AM":
            hour_end = int(hour_end) if int(hour_end) != 12 else 0
        else:
            hour_end = int(hour_end) + 12
        start = hour_start * 60 + int(minute_start)
        end = hour_end * 60 + int(minute_end)
        if search_end <= start or search_start >= end:
            continue
        else:
            resource_list_avaible.append(r)

    return index(request, [], resource_list_avaible)


def new(request):
    # a page containing the form to create a new resource
    return render(request, 'new.html')


def resource(request, resource_id=None):
    # get current resource
    current_resource = get_object_or_404(Resource, pk=resource_id)

    # check if the current resource is owned by the current user
    # and get the tags string so that the tag value can be shown as default value in the form
    my_resource = Resource.objects.filter(
        owner=users.get_current_user(),
        pk=resource_id,
    )
    edit = False
    tag_list_string = ""
    if len(my_resource) != 0:
        edit = True
        tag_list = []
        # Actually, this for-loop always has only one loop
        for r in my_resource:
            tag_list = list(r.tags.all())
        for tag in tag_list:
            tag_list_string = tag_list_string + str(tag.name) + ", "
        tag_list_string = tag_list_string[:len(tag_list_string) - 2]

    # get the reservations for current resource
    reservation_list = Reservation.objects.filter(
        resource=current_resource,
    )

    # to order the time correctly and ignore reservations that pass the time
    current = (datetime.datetime.now() + datetime.timedelta(hours=-4)).strftime('%H:%M')
    current_hour, current_minute = current.split(":")
    current_time_in_minutes = int(current_hour) * 60 + int(current_minute)
    am_helper_list = []
    pm_helper_list = []
    for reservation in reservation_list:
        time, sign = reservation.time.split(" ")
        hour, minute = time.split(":")
        if sign == "AM":
            hour = int(hour) if int(hour) != 12 else 0
            end = hour * 60 + int(minute) + int(reservation.duration) * 60
            if current_time_in_minutes <= end:
                am_helper_list.append(reservation)
        else:
            hour = int(hour) + 12
            end = hour * 60 + int(minute) + int(reservation.duration) * 60
            if current_time_in_minutes <= end:
                pm_helper_list.append(reservation)

    return render(request, 'resource.html', {
        'resource': current_resource,
        'tag_list_string': tag_list_string,
        'edit': edit,
        'reservation_list': reservation_list,
        'hour': current_hour,
        'minute': current_minute,
        'am_helper_list': am_helper_list,
        'pm_helper_list': pm_helper_list,
    })


def get_resource(request, tag_id=None):
    # use a certain tag to find all the resources that have this tag
    current_tag = get_object_or_404(Tag, pk=tag_id)
    resource_list = current_tag.resource_set.all()

    return render(request, 'tag.html', {
        'current_tag': current_tag,
        'resource_list': resource_list,
    })


def get_user(request, username=None):
    # fine the resources owned by a certain user
    resource_list = Resource.objects.filter(
        owner=username,
    )

    # find the reservation owned by a certain user
    reservation_list = Reservation.objects.filter(
        owner=username,
    )

    # to order the time correctly and ignore reservations that pass the time
    current = (datetime.datetime.now() + datetime.timedelta(hours=-4)).strftime('%H:%M')
    current_hour, current_minute = current.split(":")
    current_time_in_minutes = int(current_hour) * 60 + int(current_minute)
    am_helper_list = []
    pm_helper_list = []
    for reservation in reservation_list:
        time, sign = reservation.time.split(" ")
        hour, minute = time.split(":")
        if sign == "AM":
            hour = int(hour) if int(hour) != 12 else 0
            end = hour * 60 + int(minute) + int(reservation.duration) * 60
            if current_time_in_minutes <= end:
                am_helper_list.append(reservation)
        else:
            hour = int(hour) + 12
            end = hour * 60 + int(minute) + int(reservation.duration) * 60
            if current_time_in_minutes <= end:
                pm_helper_list.append(reservation)

    return render(request, 'user.html', {
        'username': username,
        'resource_list': resource_list,
        'reservation_list': reservation_list,
        'hour': current_hour,
        'minute': current_minute,
        'am_helper_list': am_helper_list,
        'pm_helper_list': pm_helper_list,
    })


def create_resource(request):
    # get the information about the new resource
    new_resource = Resource()
    new_resource.created = datetime.datetime.now() + datetime.timedelta(hours=-4)
    new_resource.owner = users.get_current_user()
    new_resource.name = request.POST['name'].title()
    new_resource.start = request.POST['start']
    new_resource.end = request.POST['end']
    new_resource.description = request.POST['description']
    new_resource.last = datetime.datetime.now() + datetime.timedelta(hours=-4)

    # check start and end time, start time must be earlier than the end time
    time_start, sign_start = request.POST['start'].split(" ")
    time_end, sign_end = request.POST['end'].split(" ")
    hour_start, minute_start = time_start.split(":")
    hour_end, minute_end = time_end.split(":")
    if sign_start == "PM":
        hour_start = int(hour_start) + 12
    else:
        hour_start = int(hour_start) if int(hour_start) != 12 else 0
    if sign_end == "PM":
        hour_end = int(hour_end) + 12
    else:
        hour_end = int(hour_end) if int(hour_end) != 12 else 0
    if hour_end <= hour_start:
        messages.error(request, "Create a resource: the start time should be before the end time.")
        return redirect(request.META.get('HTTP_REFERER'))

    # deal with the tags
    # if a tag doesn't exit in the Tag table, then a new tag is created before is added to the new resource
    if new_resource.name and new_resource.start and new_resource.end:
        new_resource.save()
        tags = request.POST['tags'].replace(" ", "").split(",")
        for tag in tags:
            tag = tag.title()
            old_tag = Tag.objects.filter(name=tag)
            if len(old_tag) == 0:
                new_tag = Tag()
                new_tag.name = tag
                new_tag.save()
                new_resource.tags.add(new_tag)
            else:
                new_resource.tags.add(Tag.objects.filter(name=tag)[:1].get())
        messages.success(request, "Create a resource: success.")
    else:
        messages.error(request, "Create a resource: please enter the name, start time, and end time.")

    return redirect(request.META.get('HTTP_REFERER'))


def update_resource(request, resource_id=None):
    # get the information about the resource
    current_resource = get_object_or_404(Resource, pk=resource_id)
    current_resource.name = request.POST['name'].title()
    current_resource.start = request.POST['start']
    current_resource.end = request.POST['end']
    current_resource.description = request.POST['description']

    # check start and end time, start time should be earlier than the end time
    time_start, sign_start = request.POST['start'].split(" ")
    time_end, sign_end = request.POST['end'].split(" ")
    hour_start, minute_start = time_start.split(":")
    hour_end, minute_end = time_end.split(":")
    if sign_start == "PM":
        hour_start = int(hour_start) + 12
    else:
        hour_start = int(hour_start) if int(hour_start) != 12 else 0
    if sign_end == "PM":
        hour_end = int(hour_end) + 12
    else:
        hour_end = int(hour_end) if int(hour_end) != 12 else 0
    if hour_end <= hour_start:
        messages.error(request, "Update a resource: the start time should be before the end time.")
        return redirect(request.META.get('HTTP_REFERER'))

    # check if the name, start time, and end time are entered since these fields are necessary
    # if true, then deal with the tags
    # if a tag doesn't exit in the Tag table, then a new tag is created before is added to the new resource
    if current_resource.name and current_resource.start and current_resource.end:
        current_resource.save()
        current_resource.tags.clear()
        tags = request.POST['tags'].replace(" ", "").split(",")
        for tag in tags:
            tag = tag.title()
            old_tag = Tag.objects.filter(name=tag)
            if len(old_tag) == 0:
                new_tag = Tag()
                new_tag.name = tag
                new_tag.save()
                current_resource.tags.add(new_tag)
            else:
                current_resource.tags.add(Tag.objects.filter(name=tag)[:1].get())
        messages.success(request, "Update a resource: success.")
    else:
        messages.error(request, "Update a resource: please enter the name, start time, and end time.")

    return redirect(request.META.get('HTTP_REFERER'))


def create_reservation(request, resource_id=None):
    # first, get the resource that the user is making reservation for
    current_resource = get_object_or_404(Resource, pk=resource_id)

    # get the information of the reservation
    new_reservation = Reservation()
    new_reservation.created = datetime.datetime.now() + datetime.timedelta(hours=-4)
    new_reservation.owner = users.get_current_user()
    new_reservation.resource = current_resource
    new_reservation.time = request.POST['time']
    new_reservation.duration = int(request.POST['duration'])

    # check if the duration is a integer greater than 0
    # if a decimal is used, then the largest integer that is smaller than this decimal is used
    if new_reservation.duration <= 0:
        messages.error(request, "Make a reservation: duration must be greater than 0")
        return redirect(request.META.get('HTTP_REFERER'))

    # check time is within the available hours of the resource
    time_reservation, sign_reservation = request.POST['time'].split(" ")
    time_resource_start, sign_resource_start = current_resource.start.split(" ")
    time_resource_end, sign_resource_end = current_resource.end.split(" ")
    hour_reservation, minute_reservation = time_reservation.split(":")
    hour_resource_start, minute_resource_start = time_resource_start.split(":")
    hour_resource_end, minute_resource_end = time_resource_end.split(":")
    if sign_reservation == "PM":
        hour_reservation = int(hour_reservation) + 12
    else:
        hour_reservation = int(hour_reservation) if int(hour_reservation) != 12 else 0
    if sign_resource_start == "PM":
        hour_resource_start = int(hour_resource_start) + 12
    else:
        hour_resource_start = int(hour_resource_start) if int(hour_reservation) != 12 else 0
    if sign_resource_end == "PM":
        hour_resource_end = int(hour_resource_end) + 12
    else:
        hour_resource_end = int(hour_resource_end) if int(hour_reservation) != 12 else 0
    compare_reservation_start = hour_reservation * 60 + int(minute_reservation)
    compare_reservation_end = compare_reservation_start + int(request.POST['duration']) * 60
    compare_resource_start = hour_resource_start * 60 + int(minute_resource_start)
    compare_resource_end = hour_resource_end * 60 + int(minute_resource_end)

    # check this resource is available and not booked by other people at this time
    reservation_list = Reservation.objects.filter(
        resource=current_resource,
    )
    reserved = False
    for reservation in reservation_list:
        time, sign = reservation.time.split(" ")
        hour, minute = time.split(":")
        if sign == "PM":
            hour = int(hour) + 12
        else:
            hour = int(hour) if int(hour) != 12 else 0
        start = hour * 60 + int(minute)
        end = start + int(reservation.duration) * 60
        if compare_reservation_start >= end or compare_reservation_end <= start:
            continue
        else:
            reserved = True
            break

    # check user available
    my_reservation_list = Reservation.objects.filter(
        owner=users.get_current_user()
    )
    no_time = False
    for reservation in my_reservation_list:
        time, sign = reservation.time.split(" ")
        hour, minute = time.split(":")
        if sign == "PM":
            hour = int(hour) + 12
        else:
            hour = int(hour) if int(hour) != 12 else 0
        start = hour * 60 + int(minute)
        end = start + int(reservation.duration) * 60
        if compare_reservation_start >= end or compare_reservation_end <= start:
            continue
        else:
            no_time = True
            break

    # check if this reservation should be made
    # if true, then the resource also needs to be updated: the last field and the reservation_count field
    # if success, a mail is sent to confirm that the reservation is made.
    if compare_reservation_start < compare_resource_start or compare_reservation_end > compare_resource_end:
        messages.error(request, "Make a reservation: time is not within the available hours of the resource.")
    elif reserved:
        messages.error(request, "Make a reservation: time has already been reserved.")
    elif no_time:
        messages.error(request, "Make a reservation: you have other reservations at this time.")
    else:
        new_reservation.save()
        current_resource.last = datetime.datetime.now() + datetime.timedelta(hours=-4)
        current_resource.reservation_count = current_resource.reservation_count + 1

        mail.send_mail(sender="JY <chromevoid500@gmail.com>",
                       to=users.get_current_user().email(),
                       subject="Your reservation has been made",
                       body="Hi:\n\nYou just made a new reservation.\nResource Name: " + new_reservation.resource.name + "\nTime: " + new_reservation.time + "\nDuration " + str(
                           new_reservation.duration) + "\n\nJY"
                       )
        current_resource.save()
        messages.success(request, "Make a reservation: success.")

    return redirect(request.META.get('HTTP_REFERER'))


def delete_reservation(request, reservation_id=None):
    # get the current reservation and then delete
    current_reservation = get_object_or_404(Reservation, pk=reservation_id)
    current_reservation.delete()
    messages.success(request, "Delete a reservation: success.")

    return redirect(request.META.get('HTTP_REFERER'))


# Follow the demo on https://docs.djangoproject.com/en/1.11/ref/contrib/syndication/
class ResourceReservationFeed(Feed):
    def get_object(self, request, resource_id):
        return get_object_or_404(Resource, pk=resource_id)

    def link(self, obj):
        return "Resource link"

    def title(self, obj):
        return "Reservation of %s" % obj.name

    def items(self, obj):
        return Reservation.objects.filter(resource=obj)

    def item_link(self, item):
        return "Reservation link."

    def item_title(self, item):
        return "Title (TBD)"

    def item_description(self, item):
        return "{0} : {1} - {2}".format(item.owner, item.time, item.duration)
