# Generated by Django 2.2.23 on 2022-03-27 23:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_user_desc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='desc',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='各人描述'),
        ),
    ]
