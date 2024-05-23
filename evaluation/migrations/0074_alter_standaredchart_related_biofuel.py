# Generated by Django 4.0.1 on 2022-11-03 16:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0073_standaredchart_oil'),
    ]

    operations = [
        migrations.AlterField(
            model_name='standaredchart',
            name='related_biofuel',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='related_biofuel', to='evaluation.biofuel'),
        ),
    ]