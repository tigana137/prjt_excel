# Generated by Django 4.2.7 on 2023-12-02 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('x', '0008_adminecoledata_cinquieme_data_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='levelstat',
            name='nbr_classes',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='levelstat',
            name='nbr_elvs',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
