# Generated by Django 4.2.7 on 2024-02-14 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('x', '0020_remove_del1_password_remove_del1_username_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='levelstat',
            name='nbr_comming',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='levelstat',
            name='nbr_leaving',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
