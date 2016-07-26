# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-26 17:05
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountStatusChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leaving_date', models.DateTimeField(null=True)),
                ('changed', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('AWAITING_DIRECT_DEBIT', 'Awating Go Cardless'), ('ACTIVE', 'Active'), ('LEFT', 'Left')], max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='BagType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="E.g. 'Standard veg'.", max_length=50, unique=True)),
                ('display_order', models.IntegerField(blank=True, help_text='\n        Bags will be sorted by this number.\n        ', null=True)),
                ('active', models.BooleanField(default=True, help_text='Active bags appear in the joining form.')),
            ],
            options={
                'ordering': ['display_order'],
            },
        ),
        migrations.CreateModel(
            name='BagTypeCostChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('changed', models.DateTimeField(auto_now_add=True)),
                ('weekly_cost', models.DecimalField(blank=True, decimal_places=2, help_text='Enter the weekly fee for receiving this bag.', max_digits=12, null=True, verbose_name='Weekly cost')),
                ('bag_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cost_changes', to='join.BagType')),
            ],
        ),
        migrations.CreateModel(
            name='BillingCredit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('amount_pence', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='BillingGoCardlessMandate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_token', models.CharField(default='', max_length=255)),
                ('gocardless_redirect_flow_id', models.CharField(default='', max_length=255)),
                ('gocardless_mandate_id', models.CharField(default='', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='CollectionPoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="e.g. 'The Old Fire Station'", max_length=40, unique=True)),
                ('location', models.CharField(blank=True, help_text="E.g. 'Leswin Road, N16'", max_length=100, null=True)),
                ('latitude', models.FloatField(blank=True, help_text="\n        Allows your pickup to show on a map. Latitude should be\n        between 49 and 60 in the UK. You can find latitude and longitude by\n        following these instructions: <ol><li>Go to <a\n        href='http://maps.google.co.uk/' target='_NEW'>Google\n        maps</a></li><li>Click the tiny green flask icon on the\n        top-right</li><li>Scroll down and enable the 'LatLng Tool\n        Tip'</li><li>Find your pickup and zoom in close</li><li>You'll see\n        (latitude, longitude) showing on the mouse pointer</li><li>Note them\n        down and copy latitude into the field above and longitude into the\n        field below</li></ol>\n        ", null=True)),
                ('longitude', models.FloatField(blank=True, help_text='Longitude should be between -10 and 2 in the UK', null=True)),
                ('active', models.BooleanField(default=True, help_text='\n        You can mark this pickup as not available if you need to. This might\n        be because it is full for example.\n        ')),
                ('inactive_reason', models.CharField(choices=[('FULL', 'Full'), ('CLOSING_DOWN', 'Closing down')], default='FULL', max_length=255, null=True)),
                ('collection_day', models.CharField(choices=[('WED_THURS', 'Wednesday and Thursday'), ('WED', 'Wednesday'), ('THURS', 'Thursday')], default='WED', max_length=255)),
                ('display_order', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-active', 'display_order'],
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255)),
                ('nickname', models.CharField(max_length=30)),
                ('mobile', models.CharField(blank=True, default='', max_length=30)),
                ('balance_carried_over', models.IntegerField(default=0)),
                ('holiday_due', models.IntegerField(default=0)),
                ('gocardless_current_mandate', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='in_use_for_customer', to='join.BillingGoCardlessMandate')),
            ],
        ),
        migrations.CreateModel(
            name='CustomerCollectionPointChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('changed', models.DateTimeField(auto_now_add=True)),
                ('collection_point', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='join.CollectionPoint')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='join.Customer')),
            ],
        ),
        migrations.CreateModel(
            name='CustomerOrderChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('changed', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='join.Customer')),
            ],
        ),
        migrations.CreateModel(
            name='CustomerOrderChangeBagQuantity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('bag_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='join.BagType')),
                ('customer_order_change', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bag_quantities', to='join.CustomerOrderChange')),
            ],
            options={
                'verbose_name_plural': 'customer order changes bag quantities',
            },
        ),
        migrations.CreateModel(
            name='CustomerTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ('tag',),
            },
        ),
        migrations.CreateModel(
            name='Skip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('collection_date', models.DateTimeField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='skip', to='join.Customer')),
            ],
        ),
        migrations.AddField(
            model_name='customer',
            name='tags',
            field=models.ManyToManyField(blank=True, to='join.CustomerTag'),
        ),
        migrations.AddField(
            model_name='customer',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='customer', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='billinggocardlessmandate',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='go_cardless_mandate', to='join.Customer'),
        ),
        migrations.AddField(
            model_name='billingcredit',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='billing_credit', to='join.Customer'),
        ),
        migrations.AddField(
            model_name='accountstatuschange',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='account_status_change', to='join.Customer'),
        ),
    ]
