# Generated by Django 4.0.1 on 2022-02-26 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='acordion',
            name='apps',
            field=models.CharField(choices=[('administration', 'Administration'), ('authentication-and-authorization', 'Authentication and Authorization'), ('content-types', 'Content Types'), ('sessions', 'Sessions'), ('messages', 'Messages'), ('static-files', 'Static Files'), ('sites', 'Sites'), ('accounts', 'Accounts'), ('home', 'Home'), ('evaluation', 'Evaluation'), ('crm', 'Crm'), ('doc', 'Doc')], default='', max_length=50),
            preserve_default=False,
        ),
    ]