# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-11 05:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20170711_1118'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='history',
            options={'ordering': ['-id']},
        ),
    ]
