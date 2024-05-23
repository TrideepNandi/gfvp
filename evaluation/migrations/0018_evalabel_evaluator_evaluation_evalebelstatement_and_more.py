# Generated by Django 4.0.1 on 2022-03-30 14:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('evaluation', '0017_remove_evalabel_evaluator_remove_evalabel_label_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='EvaLabel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.CharField(default=0, max_length=3)),
                ('create_date', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Evaluator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=252)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=16)),
                ('orgonization', models.CharField(max_length=252)),
                ('create_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('report_genarated', models.BooleanField(default=False)),
                ('biofuel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='evaluation.biofuel')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Evaluation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('evaluator', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='eva_evaluator', to='evaluation.evaluator')),
                ('option', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='eva_option', to='evaluation.option')),
                ('question', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='eva_question', to='evaluation.question')),
            ],
        ),
        migrations.CreateModel(
            name='EvaLebelStatement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option_id', models.CharField(blank=True, max_length=252, null=True)),
                ('statement', models.TextField(blank=True, null=True)),
                ('next_step', models.TextField(blank=True, null=True)),
                ('positive', models.CharField(default=0, max_length=1)),
                ('dont_know', models.BooleanField(default=False)),
                ('assesment', models.BooleanField(default=False)),
                ('create_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('evalebel', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='evaluation.evalabel')),
                ('evaluator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='s_evaluators', to='evaluation.evaluator')),
                ('question', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='evaluation.question')),
            ],
        ),
        migrations.AddField(
            model_name='evalabel',
            name='evaluator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='evaluators', to='evaluation.evaluator'),
        ),
        migrations.AddField(
            model_name='evalabel',
            name='label',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='labels', to='evaluation.difinedlabel'),
        ),
        migrations.CreateModel(
            name='EvaComments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comments', models.TextField(max_length=600)),
                ('evaluator', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='coment_evaluator', to='evaluation.evaluator')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='comment_question', to='evaluation.question')),
            ],
        ),
    ]