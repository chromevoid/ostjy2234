# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your models here.
from django.db import models
from django.core.validators import *


class Resource(models.Model):
    created = models.DateTimeField()
    owner = models.CharField(
        max_length=100,
        validators=[MaxLengthValidator(100)]
    )
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    start = models.CharField(max_length=10)
    end = models.CharField(max_length=10)
    tags = models.CharField(max_length=100)
    last = models.DateTimeField()


class Reservation(models.Model):
    created = models.DateTimeField()
    owner = models.CharField(max_length=20)
    resource = models.ForeignKey(Resource)
    time = models.CharField(max_length=10)
    duration = models.IntegerField(default=0)
