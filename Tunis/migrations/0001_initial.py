# Generated by Django 4.2.7 on 2024-03-15 15:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Class',
            fields=[
                ('cid', models.IntegerField(primary_key=True, serialize=False)),
                ('class_name', models.CharField(max_length=100)),
                ('class_level', models.IntegerField(choices=[(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6')])),
                ('level', models.IntegerField(choices=[(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6')])),
            ],
        ),
        migrations.CreateModel(
            name='Dre',
            fields=[
                ('id', models.PositiveSmallIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('username', models.CharField(blank=True, max_length=50, null=True)),
                ('password', models.CharField(blank=True, max_length=50, null=True)),
                ('dre_id_in_cnte', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Ecoles',
            fields=[
                ('sid', models.IntegerField(primary_key=True, serialize=False)),
                ('school_name', models.CharField(max_length=100)),
                ('principal', models.CharField(blank=True, max_length=100, null=True)),
                ('dre', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ecoles', to='Tunis.dre')),
            ],
        ),
        migrations.CreateModel(
            name='AdminElvs',
            fields=[
                ('uid', models.BigIntegerField(primary_key=True, serialize=False)),
                ('nom_prenom', models.CharField(max_length=200)),
                ('dirty_name', models.CharField(max_length=200)),
                ('classe', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Tunis.class')),
                ('ecole', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Tunis.ecoles')),
            ],
        ),
    ]