# Generated by Django 3.1.6 on 2021-02-20 05:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20210220_0500'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='Loc',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='main.loc'),
        ),
    ]