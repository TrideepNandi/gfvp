# Generated by Django 4.0.1 on 2022-04-16 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0085_alter_lead_confirm_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lead',
            name='confirm_code',
            field=models.CharField(default='127009516517', max_length=50),
        ),
    ]