# Generated by Django 3.2.7 on 2021-10-11 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsletter', '0002_newsshot_note'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsshot',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
