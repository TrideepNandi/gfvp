# Generated by Django 4.0.1 on 2022-02-24 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0019_remove_usertype_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertype',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]