# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-08 10:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('join', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reminder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(max_length=30)),
                ('date', models.DateField(blank=True, null=True)),
                ('details', models.TextField(blank=True, null=True)),
                ('done', models.BooleanField(default=False)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='join.Customer')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
    ]