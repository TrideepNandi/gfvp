# Generated by Django 4.0.1 on 2022-06-24 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0138_alter_lead_confirm_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lead',
            name='confirm_code',
            field=models.CharField(default='988076174095', max_length=50),
        ),
    ]