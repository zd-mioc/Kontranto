from django.db import models
 
class Game(models.Model):
    id=models.IntegerField(primary_key=True) #ovo je pk od Game-a, jer ForeignKey prima integer, pa ce se Move ovim povezati
    game=models.CharField(max_length=200)
    white_player_id=models.CharField(max_length=200)
    black_player_id=models.CharField(max_length=200)
    white_score=models.IntegerField()
    black_score=models.IntegerField()
    board=models.JSONField()
    game_state=models.CharField(max_length=200)
    locked=models.JSONField()

class Move(models.Model):
    game=models.ForeignKey(Game, on_delete=models.CASCADE)
    color=models.CharField(max_length=200)
    triangle_position=models.CharField(max_length=10)
    circle_position=models.CharField(max_length=10)
    move_timestamp=models.DateTimeField()
    null_fields=models.JSONField()
