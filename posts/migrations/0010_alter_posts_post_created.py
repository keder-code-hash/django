# Generated by Django 3.2.6 on 2021-10-14 21:45

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_alter_posts_post_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='posts',
            name='post_created',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 15, 3, 15, 14, 43788)),
        ),
    ]
