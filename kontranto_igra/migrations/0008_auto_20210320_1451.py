# Generated by Django 3.1.7 on 2021-03-20 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kontranto_igra', '0007_auto_20210105_2333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
