# Generated by Django 3.1.4 on 2021-01-05 21:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kontranto_igra', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='move',
            name='game_id',
            field=models.ForeignKey(db_column='game_id', on_delete=django.db.models.deletion.CASCADE, to='kontranto_igra.game'),
        ),
    ]
