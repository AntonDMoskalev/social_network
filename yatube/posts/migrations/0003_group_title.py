# Generated by Django 2.2.9 on 2021-06-25 02:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20210625_0914'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='title',
            field=models.TextField(default=str),
            preserve_default=False,
        ),
    ]
