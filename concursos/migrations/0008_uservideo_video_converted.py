# Generated by Django 3.0.3 on 2020-02-12 03:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('concursos', '0007_auto_20200212_0341'),
    ]

    operations = [
        migrations.AddField(
            model_name='uservideo',
            name='video_converted',
            field=models.CharField(blank=True, max_length=114),
        ),
    ]
