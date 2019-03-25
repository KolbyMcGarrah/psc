# Generated by Django 2.1.5 on 2019-03-03 21:33

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0007_tournament_tournament_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='playerresults',
            name='added_on',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
