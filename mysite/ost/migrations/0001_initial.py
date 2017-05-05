# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-04 05:09
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField()),
                ('owner', models.CharField(max_length=20)),
                ('time', models.CharField(max_length=10)),
                ('duration', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField()),
                ('owner', models.CharField(max_length=20, validators=[django.core.validators.MaxLengthValidator(20)])),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=100)),
                ('start', models.CharField(max_length=10)),
                ('end', models.CharField(max_length=10)),
                ('tags', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='reservation',
            name='resource',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ost.Resource'),
        ),
    ]