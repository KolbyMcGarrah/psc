# Generated by Django 2.1.5 on 2019-05-01 02:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20190224_0846'),
    ]

    operations = [
        migrations.AddField(
            model_name='proshop',
            name='section',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Alabama'), (2, 'Colorado'), (3, 'Carolinas'), (4, 'Georgia'), (5, 'Central New York'), (6, 'Illinois'), (7, 'Connecticut'), (8, 'Iowa'), (9, 'Gateway'), (10, 'Metropolitan NY'), (11, 'Gulf States'), (12, 'Middle Atlantic'), (13, 'Indiana'), (14, 'Minnesota'), (15, 'Kentucky'), (16, 'New England'), (17, 'Michigan'), (18, 'North Florida'), (19, 'Midwest'), (20, 'Northern California'), (21, 'Nebraska'), (22, 'Northern Texas'), (23, 'New Jersey'), (24, 'Philadelphia'), (25, 'Northeastern New York'), (26, 'South Central'), (27, 'Northern Ohio'), (28, 'Southern California'), (29, 'Pacific Northwest'), (30, 'Southern Texas'), (31, 'Rocky Mountain'), (32, 'Sun County'), (33, 'South Florida'), (34, 'Southern Ohio'), (35, 'Tri-State'), (36, 'Southwest'), (37, 'Western New York'), (38, 'Tennessee'), (39, 'Utah'), (40, 'Wisconsin'), (41, 'Aloha')], default=1),
        ),
    ]
