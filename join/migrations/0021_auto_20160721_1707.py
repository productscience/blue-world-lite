# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-21 17:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('join', '0020_auto_20160720_1053'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountstatuschange',
            name='leaving_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='collectionpoint',
            name='collection_day',
            field=models.CharField(choices=[('WED_THURS', 'Wednesday and Thursday'), ('WED', 'Wednesday'), ('THURS', 'Thursday')], default='WED', max_length=255),
        ),
        migrations.AlterField(
            model_name='accountstatuschange',
            name='status',
            field=models.CharField(choices=[('AWAITING_DIRECT_DEBIT', 'Awating Go Cardless'), ('ACTIVE', 'Active'), ('LEAVING', 'Leaving'), ('LEFT', 'Left')], max_length=255),
        ),
    ]
