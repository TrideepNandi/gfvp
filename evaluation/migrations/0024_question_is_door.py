# Generated by Django 4.0.1 on 2022-04-01 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0023_alter_question_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='is_door',
            field=models.BooleanField(default=False),
        ),
    ]