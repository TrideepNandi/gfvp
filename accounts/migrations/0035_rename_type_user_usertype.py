# Generated by Django 4.0.1 on 2023-01-30 09:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0034_user_newsletter_subscription'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='type',
            new_name='usertype',
        ),
    ]