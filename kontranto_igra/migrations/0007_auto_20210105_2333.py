# Generated by Django 3.1.4 on 2021-01-05 22:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kontranto_igra', '0006_auto_20210105_2321'),
    ]

    operations = [
        migrations.RenameField(
            model_name='game',
            old_name='gamid',
            new_name='game',
        ),
    ]
