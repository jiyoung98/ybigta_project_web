# Generated by Django 3.1.6 on 2021-02-26 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20210226_0809'),
    ]

    operations = [
        migrations.AddField(
            model_name='cafe',
            name='coffeescore',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cafe',
            name='pricescore',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cafe',
            name='servicescore',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cafe',
            name='vibescore',
            field=models.FloatField(blank=True, null=True),
        ),
    ]