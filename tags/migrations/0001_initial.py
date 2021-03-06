# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-26 06:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        # ('repos', '0010_remove_repository_admins'),
        ('repos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(unique=True)),
                ('active', models.BooleanField(default=True)),
                ('repos', models.ManyToManyField(blank=True, to='repos.Repository')),
            ],
        ),
    ]
