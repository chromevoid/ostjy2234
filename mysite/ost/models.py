# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your models here.
from django.db import models
from django.core.validators import *


class Tag(models.Model):
    name = models.CharField(
        max_length=100,
        validators=[MaxLengthValidator(100)]
    )


class Resource(models.Model):
    created = models.DateTimeField()
    owner = models.CharField(
        max_length=100,
        validators=[MaxLengthValidator(100)]
    )
    name = models.CharField(
        max_length=100,
        validators=[MaxLengthValidator(100)]
    )
    description = models.CharField(
        default="",
        max_length=100,
        validators=[MaxLengthValidator(100)]
    )
    start = models.CharField(
        max_length=100,
        validators=[MaxLengthValidator(100)]
    )
    end = models.CharField(
        max_length=100,
        validators=[MaxLengthValidator(100)]
    )
    tags = models.ManyToManyField(Tag)
    last = models.DateTimeField()


class Reservation(models.Model):
    created = models.DateTimeField()
    owner = models.CharField(
        max_length=100,
        validators=[MaxLengthValidator(100)]
    )
    resource = models.ForeignKey(Resource)
    time = models.CharField(
        max_length=100,
        validators=[MaxLengthValidator(100)]
    )
    duration = models.IntegerField(default=0)
