# Generated by Django 4.0.6 on 2022-08-17 00:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chemblog', '0004_comment_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='modify_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='modify_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
