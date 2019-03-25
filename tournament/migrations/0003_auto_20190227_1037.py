# Generated by Django 2.1.5 on 2019-02-27 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0002_tournament_number_of_players'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playerresults',
            name='amount_won',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True),
        ),
        migrations.AlterField(
            model_name='playerresults',
            name='position',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
