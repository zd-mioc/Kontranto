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

    # Initial placement of the pieces on the board
    INITIAL_PLACEMENT = enum.auto()

    # The players are moving their figures.
    GAME_RUNNING = enum.auto()

    # NOTE: one player must not know if the other submitted the move or
    # not. Instead these two WAITING_PLAYER_X_MOVE the client gets either:
    #  GAME_RUNNING
    #  WAITING_OTHER_PLAYER_MOVE
    # The second player submitted the next move. Waiting for the first player.
    WAITING_PLAYER_ONE_MOVE = enum.auto()
    # The first player submitted the next move. Waiting for the second player.
    WAITING_PLAYER_TWO_MOVE = enum.auto()

    # A clash between figures occured.
    CLASH = enum.auto()

    # Shock move triggered.
    SHOCK_MOVE = enum.auto()


def default_board():
    """Content of the new (empty) board."""
    return [[""] * 4] * 4


class Game(models.Model):
    game_id = models.UUIDField(primary_key=True,
                               default=uuid.uuid4,
                               editable=False)
    player_1_id = models.CharField(max_length=200)
    player_2_id = models.CharField(max_length=200, default="")
    player_1_color_choice = models.CharField(max_length=10, default="")
    player_2_color_choice = models.CharField(max_length=10, default="")
    white_player_id = models.CharField(max_length=200, default="")
    black_player_id = models.CharField(max_length=200, default="")
    # The player who won the game
    winner_id = models.CharField(max_length=200, default="")

    white_player_score = models.IntegerField(default=0)
    black_player_score = models.IntegerField(default=0)
    # 4x4 grid with the following fields:
    #  '' -- empty field
    #  WT -- white triangle
    #  WC -- white circle
    #  BT -- black triangle
    #  BC -- black circle
    #  SF -- shock field
    #  DF -- destroyed field
    # In clash, all combinations:
    #  CWTBT -- WT+BT in clash
    #  CWTBC
    #  CWCBT
    #  CWCBC
    # When player sent new move, but it's not yet official
    # (waiting for the other player's move):
    #  NWT -- next white triangle
    #  NWC -- next white circle
    #  NBT -- next black triangle
    #  NBC -- next black circle
    # These are not for the clients.
    board = models.JSONField(default=default_board)

    possible_states = [(s.name, s.name) for s in GameState]
    game_state = models.CharField(max_length=50, choices=possible_states)


class Move(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player_id = models.CharField(max_length=200)
    # Board position. Tuple (x,y)
    triangle_position = models.JSONField()
    # Board position. Tuple (x,y)
    circle_position = models.JSONField()
    move_timestamp = models.DateTimeField()
    # ID of the player who scored upon this move
    scoring_player_id = models.CharField(max_length=200, default="")
