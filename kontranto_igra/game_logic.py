import enum
import logging

from dataclasses import dataclass
from typing import Dict, List, Tuple
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.utils import timezone

from kontranto_igra.models import Game, Move, GameState

logger = logging.getLogger(__name__)

class PlayerColor(enum.Enum):
  """All possible player colors."""
  WHITE = enum.auto()
  BLACK = enum.auto()

@dataclass
class UserInput:
  """Wrapper for the user provided input."""
  player_id: str
  game_id: str = None
  color_choice_shape: str = None
  # Coordinates for the new triangle, e.g. (0, 2)
  new_triangle_position: Tuple[int, int] = None
  # Coordinates for the new circle, e.g. (3, 1)
  new_circle_position: Tuple[int, int] = None

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

  info_message: str = None
  error_message: str = None

  @staticmethod
  def from_game(game: Game):
    gr = GameResponse(game_id=str(game.game_id), game_state = game.game_state, white_player_score=game.white_player_score, black_player_score=game.black_player_score, board = game.board)
    return gr

  @staticmethod
  def from_error(error_message: str):
    return GameResponse().with_error(error_message)

  def with_error(self, error_message: str):
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
    return GameResponse.from_game(g).with_error("Illegal game state.")
  if g.player_1_id == player_id:
    return GameResponse.from_game(g).with_error("You can't join your own game!")

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


def _handle_color_choice(user_input: UserInput, g: Game) -> GameResponse:
  """Resolves color choice move."""
  if not user_input.color_choice_shape:
    return GameResponse.from_game(g).with_error("Missing color choice!")
  if user_input.player_id == g.player_1_id:
    if g.player_1_color_choice != '' and g.player_1_color_choice != user_input.color_choice_shape:
      return GameResponse.from_game(g).with_error("The color choice is already stored!")
    g.player_1_color_choice = user_input.color_choice_shape
    g.save()
  elif user_input.player_id == g.player_2_id:
    if g.player_2_color_choice != '' and g.player_2_color_choice != user_input.color_choice_shape:
      return GameResponse.from_game(g).with_error("The color choice is already stored!")
    g.player_2_color_choice = user_input.color_choice_shape
    g.save()
  else:
    return GameResponse.from_game(g).with_error("Invalid player ID!")

  # If both color choices are submitted move to the next state
  if g.player_1_color_choice != '' and g.player_2_color_choice != '':
    g.game_state = GameState.INITIAL_PLACEMENT.name
    if g.player_1_color_choice == g.player_2_color_choice:
      g.white_player_id = g.player_1_id
      g.black_player_id = g.player_2_id
    else:
      g.white_player_id = g.player_2_id
      g.black_player_id = g.player_1_id
    g.save()
  return GameResponse.from_game(g)


def _handle_piece_move(user_input: UserInput, g: Game) -> GameResponse:
  """Resolves moving of the Kontranto pieces."""
  if not user_input.new_triangle_position or not user_input.new_circle_position:
    return GameResponse.from_game(g).with_error("Missing new piece positions!")
  valid_coordinates = lambda coord: (len(coord) == 2 and 0 <= coord[0] <= 3 and 0 <= coord[1] <= 3)
  if (not valid_coordinates(user_input.new_circle_position)
        or not valid_coordinates(user_input.new_triangle_position)):
    return GameResponse.from_game(g).with_error("Invalid coordinates: " + str(user_input.new_circle_position) + " " + str(user_input.new_triangle_position))

  color = None
  if user_input.player_id == g.white_player_id:
    color = PlayerColor.WHITE
  elif user_input.player_id == g.black_player_id:
    color = PlayerColor.BLACK
  else:
    return GameResponse.from_game(g).with_error("Invalid player")

  if g.game_state in [GameState.INITIAL_PLACEMENT.name, GameState.GAME_RUNNING.name, GameState.CLASH.name]:
    if user_input.player_id == g.player_1_id:
      g.game_state = GameState.WAITING_PLAYER_TWO_MOVE.name
    else:
      g.game_state = GameState.WAITING_PLAYER_ONE_MOVE.name
  elif g.game_state in [GameState.WAITING_PLAYER_ONE_MOVE.name, GameState.WAITING_PLAYER_TWO_MOVE.name]:
    g.game_state = GameState.GAME_RUNNING.name

  color_code = "W" if color == PlayerColor.WHITE else "B"
  tx, ty = user_input.new_triangle_position
  g.board[ty][tx] = color_code + "T"
  cx, cy = user_input.new_circle_position
  g.board[cy][cx] = color_code + "C"
  g.save()
  # TODO is valid move

  # TODO timeout
  # TODO clash
  return GameResponse.from_game(g)



def handle_game_action(user_input: UserInput) -> GameResponse:
  """Plays the move and returns the new game state."""
  try:
    g = Game.objects.get(game_id = user_input.game_id)
  except ObjectDoesNotExist:
    return GameResponse(game_id=user_input.game_id).with_error("Invalid game ID")
  if user_input.player_id != g.player_1_id and user_input.player_id != g.player_2_id:
    return GameResponse.from_game(g).with_error("Invalid player!")

  # TODO: player_id must be valid
  state = g.game_state
  # Convert to the enum state
  for s in GameState:
    if state == s.name:
      state = s
      break
  else:
    return GameResponse(game_id=user_input.game_id).with_error("Invalid game state: " + state)

  if state == GameState.GAME_RUNNING:
    return _handle_piece_move(user_input, g)
  elif state == GameState.COLOR_CHOICE:
    return _handle_color_choice(user_input, g)
  elif state == GameState.INITIAL_PLACEMENT:
    return _handle_piece_move(user_input, g)
  elif state == GameState.WAITING_PLAYER_ONE_MOVE:
    return _handle_piece_move(user_input, g)
  elif state == GameState.WAITING_PLAYER_TWO_MOVE:
    return _handle_piece_move(user_input, g)
  elif state == GameState.SHOCK_MOVE:
    pass
  elif state == GameState.CLASH:
    pass
  elif state == GameState.FINISHED:
    pass
  else:
    return GameResponse(game_id=user_input.game_id).with_error("Invalid game state for this action: " + state)
