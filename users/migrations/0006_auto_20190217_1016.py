# Generated by Django 2.1.5 on 2019-02-17 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20190216_1218'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='isBuyer',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customuser',
            name='isPlayer',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customuser',
            name='isShop',
            field=models.BooleanField(default=False),
        ),
    ]
