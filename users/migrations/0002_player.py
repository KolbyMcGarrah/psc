# Generated by Django 2.1.5 on 2019-02-06 23:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='player',
            fields=[
                ('player_id', models.AutoField(primary_key=True, serialize=False)),
                ('address', models.CharField(max_length=50)),
                ('phoneNumber', models.CharField(max_length=10)),
                ('homeCourse', models.CharField(max_length=50)),
                ('insrt_timestamp', models.DateField(auto_now_add=True)),
                ('chnge_timestamp', models.DateField(auto_now=True)),
            ],
        ),
    ]
