# Generated by Django 4.0.1 on 2023-01-30 09:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0090_alter_evaluator_orgonization_alter_evaluator_phone'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='difinedlabel',
            options={'verbose_name': 'Defined Label', 'verbose_name_plural': 'Defined Labels'},
        ),
        migrations.AlterModelOptions(
            name='evalebelstatement',
            options={'verbose_name': 'Eva Label Statement', 'verbose_name_plural': 'Eva Label Statements'},
        ),
        migrations.AlterModelOptions(
            name='labeldatahistory',
            options={'verbose_name': 'Label Data History', 'verbose_name_plural': 'Label Data Histories'},
        ),
        migrations.AlterModelOptions(
            name='nextactivities',
            options={'verbose_name': 'Next Activity', 'verbose_name_plural': 'Next Activities'},
        ),
        migrations.AlterModelOptions(
            name='olilist',
            options={'verbose_name': 'Oil List', 'verbose_name_plural': 'Oil Lists'},
        ),
        migrations.AlterModelOptions(
            name='standaredchart',
            options={'verbose_name': 'Standard Chart', 'verbose_name_plural': 'Standard Charts'},
        ),
        migrations.AlterModelOptions(
            name='stdoils',
            options={'verbose_name': 'Std Oil', 'verbose_name_plural': 'Std Oils'},
        ),
    ]