# Generated by Django 2.1.5 on 2019-04-13 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0011_playerresults_flight'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='prize_pool',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=11, null=True),
        ),
    ]
