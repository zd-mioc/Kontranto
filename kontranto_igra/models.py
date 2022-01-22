import enum
import uuid

from django.db import models


class GameState(enum.Enum):
  """All possible game states."""
  # Game is created, but still missing the second player.
  GAME_SETUP = enum.auto()
  # The game is done. No further action is possible.
  FINISHED = enum.auto()
  # Both players are present. First play step: color choice
  COLOR_CHOICE = enum.auto()
  # The players are moving their figures.
  GAME_RUNNING = enum.auto()
  # The black player submitted the next move. Waiting for the white.
  WAITING_WHITE_PLAYER_MOVE = enum.auto()
  # The white player submitted the next move. Waiting for the black.
  WAITING_BLACK_PLAYER_MOVE = enum.auto()
  # A clash between figures occured.
  CLASH = enum.auto()
  # Shock move triggered.
  SHOCK_MOVE = enum.auto()


def default_board():
  """Content of the new (empty) board."""
  return [[""]*4]*4

class Game(models.Model):
  game_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  player_1_id=models.CharField(max_length=200)
  player_2_id=models.CharField(max_length=200)
  white_player_id=models.CharField(max_length=200)
  black_player_id=models.CharField(max_length=200)

  white_player_score=models.IntegerField(default=0)
  black_player_score=models.IntegerField(default=0)
  # 4x4 grid with the following fields:
  #  '' -- empty field
  #  WT -- white triangle
  #  WC -- white circle
  #  BT -- black triangle
  #  BC -- black circle
  #  SF -- shock field
  #  DF -- destroyed field
  # When player sent new move, but it's not yet official
  # (waiting for the other player's move):
  #  NWT -- next white triangle
  #  NWC -- next white circle
  #  NBT -- next black triangle
  #  NBC -- next black circle
  # These are not for the clients.
  board=models.JSONField(default=default_board)

  possible_states = [(s.name, s.name) for s in GameState]
  game_state=models.CharField(max_length=50, choices=possible_states)

class Move(models.Model):
  game_id=models.ForeignKey(Game, on_delete=models.CASCADE)
  color=models.CharField(max_length=200)
  triangle_position=models.CharField(max_length=10)
  circle_position=models.CharField(max_length=10)
  move_timestamp=models.DateTimeField()
