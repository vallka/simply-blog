# Generated by Django 3.1.6 on 2021-02-25 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_post_email_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-id']},
        ),
        migrations.AddField(
            model_name='post',
            name='title_bgcolor',
            field=models.CharField(blank=True, default='', max_length=20, verbose_name='Title Bg Color'),
        ),
        migrations.AddField(
            model_name='post',
            name='title_color',
            field=models.CharField(blank=True, default='', max_length=20, verbose_name='Title Color'),
        ),
    ]
