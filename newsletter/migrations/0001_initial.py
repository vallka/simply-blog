# Generated by Django 3.1.2 on 2020-11-10 19:03

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('blog', '0008_post_email_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsShot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid1, unique=True)),
                ('customer_id', models.IntegerField(db_index=True)),
                ('send_dt', models.DateTimeField(blank=True, null=True)),
                ('received_dt', models.DateTimeField(blank=True, null=True)),
                ('opened_dt', models.DateTimeField(blank=True, null=True)),
                ('clicked_dt', models.DateTimeField(blank=True, null=True)),
                ('clicked_qnt', models.IntegerField(blank=True, null=True)),
                ('blog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.post')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
    ]
