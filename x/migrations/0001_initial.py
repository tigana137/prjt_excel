# Generated by Django 4.2.7 on 2023-11-05 14:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdminEcoledata2',
            fields=[
                ('sid', models.IntegerField(primary_key=True, serialize=False)),
                ('school_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Del1',
            fields=[
                ('id', models.PositiveSmallIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Dre',
            fields=[
                ('id', models.PositiveSmallIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='AdminElvs',
            fields=[
                ('uid', models.BigIntegerField(primary_key=True, serialize=False)),
                ('nom_prenom', models.CharField(max_length=200)),
                ('nom_pere', models.CharField(max_length=200)),
                ('date_naissance', models.DateField(blank=True, null=True)),
                ('ecole', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='x.adminecoledata2')),
            ],
        ),
        migrations.AddField(
            model_name='adminecoledata2',
            name='del1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='x.del1'),
        ),
        migrations.AddField(
            model_name='adminecoledata2',
            name='dre',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='x.dre'),
        ),
    ]
