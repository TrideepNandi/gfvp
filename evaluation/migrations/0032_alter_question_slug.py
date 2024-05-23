# Generated by Django 4.0.1 on 2022-04-04 13:36

from django.db import migrations, models
import evaluation.models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0031_remove_question_parent_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='slug',
            field=models.CharField(default=evaluation.models.generate_uuid, editable=False, max_length=40),
        ),
    ]