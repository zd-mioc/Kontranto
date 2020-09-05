from django.db import models
 
class Game(models.Model):
    game_id=models.CharField(max_length=200)
    white_player_id=models.CharField(max_length=200)
    black_player_id=models.CharField(max_length=200)
    white_score=models.IntegerField()
    black_score=models.IntegerField()
    white_triangle_position=models.CharField(max_length=200)
    black_triangle_postition=models.CharField(max_length=200)
    white_circle_position=models.CharField(max_length=200)
    black_circle_position=models.CharField(max_length=200)

class Move(models.Model):
    game_id=models.ForeignKey("game", on_delete=models.CASCADE)
    white_triangle_position=models.CharField(max_length=200)
    black_triangle_postion=models.CharField(max_length=200)
    white_circle_position=models.CharField(max_length=200)
    black_circle_position=models.CharField(max_length=200)
    last_move_white_timestamp=models.DateTimeField()
    last_move_black_timestamp=models.DateTimeField()
