# Generated by Django 4.2.7 on 2024-03-20 07:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('x', '0031_alter_del1_dre'),
    ]

    operations = [
        migrations.AlterField(
            model_name='del1',
            name='dre',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Del1s', to='x.dre'),
        ),
    ]
