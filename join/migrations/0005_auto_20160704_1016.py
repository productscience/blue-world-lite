# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-04 10:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('join', '0004_auto_20160704_0902'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CollectionPointChange',
            new_name='CustomerCollectionPointChange',
        ),
        migrations.RenameModel(
            old_name='OrderChange',
            new_name='CustomerOrderChange',
        ),
        migrations.AlterModelOptions(
            name='bagquantity',
            options={'verbose_name_plural': 'bag quantities'},
        ),
        migrations.RenameField(
            model_name='bagquantity',
            old_name='order_change',
            new_name='customer_order_change',
        ),
    ]
