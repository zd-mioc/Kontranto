# Generated by Django 3.1.4 on 2020-12-22 20:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_id', models.CharField(max_length=200)),
                ('white_player_id', models.CharField(max_length=200)),
                ('black_player_id', models.CharField(max_length=200)),
                ('white_score', models.IntegerField()),
                ('black_score', models.IntegerField()),
                ('board', models.JSONField()),
                ('game_state', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Move',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(max_length=200)),
                ('triangle_position', models.CharField(max_length=10)),
                ('circle_position', models.CharField(max_length=10)),
                ('move_timestamp', models.DateTimeField()),
                ('game_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kontranto_igra.game')),
            ],
        ),
    ]
