# Generated by Django 4.2.7 on 2024-03-11 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('x', '0025_names'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tuniselvs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.BigIntegerField()),
                ('nom_prenom', models.CharField(max_length=200)),
                ('classe_id', models.CharField(max_length=200)),
                ('ecole_name', models.CharField(max_length=200)),
                ('ecole_id', models.IntegerField()),
            ],
        ),
        migrations.DeleteModel(
            name='names',
        ),
    ]
