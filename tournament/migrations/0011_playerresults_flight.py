# Generated by Django 2.1.5 on 2019-04-11 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0010_auto_20190321_1935'),
    ]

    operations = [
        migrations.AddField(
            model_name='playerresults',
            name='flight',
            field=models.CharField(blank=True, default='', max_length=25),
        ),
    ]
