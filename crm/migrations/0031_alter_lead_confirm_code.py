# Generated by Django 4.0.1 on 2022-03-25 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0030_alter_lead_confirm_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lead',
            name='confirm_code',
            field=models.CharField(default='076751867565', max_length=50),
        ),
    ]