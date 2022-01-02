import enum
import logging

from dataclasses import dataclass
from typing import Dict, List
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.utils import timezone

from kontranto_igra.models import Game, Move, GameState

logger = logging.getLogger(__name__)

@dataclass
class UserInput:
  """Wrapper for the user provided input."""
  player_id: str
  game_id: str = None
  color_choice_shape: str = None
  new_triangle_position: str = None
  new_circle_position: str = None

  @staticmethod
  def from_dict(in_dict: Dict[str, str]):
    """Returns the UserInput built from """
    user_input = UserInput(in_dict['player_id'])
    user_input.game_id = in_dict.get('game_id', None)
    user_input.color_choice_shape = in_dict.get('color_choice_shape', None)
    user_input.new_triangle_position = in_dict.get('new_triangle_position', None)
    user_input.new_circle_position = in_dict.get('new_circle_position', None)
    return user_input

@dataclass
class GameResponse:
  """Response data to send back to the user."""
  game_id: str = None
  game_state: str = None

  current_player_color: str = ""
  opponent_player_id: str = None
  white_player_score: int = 0
  black_player_score: int = 0

  board: List[List[str]] = None

  response_status: str = "OK"
  error_message: str = None

  @staticmethod
  def from_game(game: Game):
    gr = GameResponse(game_id=str(game.game_id), game_state = game.game_state, white_player_score=game.white_player_score, black_player_score=game.black_player_score, board = game.board)
    return gr

  @staticmethod
  def from_error(error_message: str):
    return GameResponse().with_error(error_message)

  def with_error(self, error_message: str):
    self.response_status = "ERROR"
    self.error_message = error_message
    return self

def create_game(player_id) -> GameResponse:
  """Creates a new game and returns its ID."""
  g = Game.objects.create(player_1_id = player_id, game_state = GameState.GAME_SETUP.name)
  g.save()
  return GameResponse.from_game(g)


def join_game(player_id, game_id) -> GameResponse:
  """Joins a new player to the game."""
  try:
    g = Game.objects.get(game_id = game_id)
  except ObjectDoesNotExist:
    return GameResponse(game_id=game.game_id).with_error("Invalid game ID")

  # Validation
  if g.game_state != GameState.GAME_SETUP.name:
    return GameResponse(game_id=g.game_id).with_error("Illegal game state.")
  if g.player_1_id == player_id:
    return GameResponse(game_id=g.game_id).with_error("You can't join your own game!")

  # Update the game state
  g.player_2_id = player_id
  g.game_state = GameState.COLOR_CHOICE.name
  g.save()
  return GameResponse.from_game(g)

def get_game_state(player_id, game_id) -> GameResponse:
  """Returns the game metadata."""
  try:
    g = Game.objects.get(game_id = game_id)
  except ObjectDoesNotExist:
    return GameResponse(game_id=game.game_id).with_error("Invalid game ID")

  gr = GameResponse.from_game(g)

  # Set the color if it's decided
  if g.black_player_id == player_id:
    gr.current_player_color = "BLACK"
  elif g.white_player_id == player_id:
    gr.current_player_color = "WHITE"

  gr.opponent_player_id = g.player_2_id if g.player_1_id == player_id else g.player_1_id
  return gr

def handle_game_action(user_input: UserInput) -> GameResponse:
  """Plays the move and returns the new game state."""
  try:
    g = Game.objects.get(game_id = user_input.game_id)
  except ObjectDoesNotExist:
    return GameResponse(game_id=user_input.game_id).with_error("Invalid game ID")

  # TODO: player_id must be valid
  state = g.game_state
  # Convert to the enum state
  for s in GameState:
    if state == s.name:
      state = s
      break
  else:
    return GameResponse(game_id=user_input.game_id).with_error("Invalid game state: {state}")

  if state == GameState.GAME_RUNNING:
    pass
  elif state == GameState.SHOCK_MOVE:
    pass
  elif state == GameState.CLASH:
    pass
  elif state == GameState.FINISHED:
    pass
  else:
    return GameResponse(game_id=user_input.game_id).with_error("Invalid game state for this action: {state}")
