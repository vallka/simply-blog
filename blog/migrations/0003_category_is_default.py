# Generated by Django 3.1 on 2020-08-28 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='is_default',
            field=models.BooleanField(default=False, verbose_name='Default Category'),
        ),
    ]