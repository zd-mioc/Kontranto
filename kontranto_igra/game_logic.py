import datetime
import enum
import json
import logging

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from django.core.exceptions import ObjectDoesNotExist

from kontranto_igra.models import Game, Move, GameState

logger = logging.getLogger(__name__)

# Maximum allowed time for move per player
MAX_TIME_PER_MOVE = datetime.timedelta(minutes=5)

# The number of points to win the game
WINNING_SCORE = 9

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


def _find_board_field(g: Game, content: str) -> Tuple[Optional[int], Optional[int]]:
  """Returns the coordinates of the board field with the given figure"""
  for y, row in enumerate(g.board):
    for x, field in enumerate(row):
      if field == content:
        return (x, y)
  return (None, None)


def _can_visit_all_figures(g: Game) -> bool:
  """Returns true if all figures are reachable from each other"""
  x,y = _find_board_field(g, "WT")
  target = set(["WT", "WC", "BT", "BC"])
  found = []
  to_visit = []
  visited = set()
  while True:
    if g.board[y][x] in target:
      found.append(g.board[y][x])
      if len(found) == len(target):
        return True
    visited.add((x,y))
    valid_x = [x]
    valid_y = [y]
    if x-1 >= 0:
      valid_x.append(x-1)
    if x+1 < len(g.board):
      valid_x.append(x+1)
    if y-1 >= 0:
      valid_y.append(y-1)
    if y+1 < len(g.board):
      valid_y.append(y+1)
    for nx in valid_x:
      for ny in valid_y:
        if (nx, ny) not in visited and (nx, ny) not in to_visit and g.board[y][x] != "DF":
          to_visit.append((x,y))
    if not to_visit:
      break
    x,y = to_visit.pop()
  return False


def _clear_board_field(g: Game, content: str):
  """Clears the board field populated with the given content"""
  (x, y) = _find_board_field(g, content)
  if x is None or y is None:
    return
  g.board[y][x] = ''


def _check_clash_and_update_game(g: Game, current_player_color: PlayerColor, new_triangle_position: Tuple[int, int], new_circle_position: Tuple[int, int]) -> str:
  """Checks if there's a clash. Updates the game and returns the ID of scoring player (or an empty string)"""
  current_player_color_code = "W" if current_player_color == PlayerColor.WHITE else "B"
  other_player_color_code = "B" if current_player_color == PlayerColor.WHITE else "W"

  # Remove the N-prefix from the other player's position
  (other_tx, other_ty) = _find_board_field(g, "N"+other_player_color_code+"T")
  (other_cx, other_cy) = _find_board_field(g, "N"+other_player_color_code+"C")
  g.board[other_ty][other_tx] = other_player_color_code + "T"
  g.board[other_cy][other_cx] = other_player_color_code + "C"

  tx, ty = new_triangle_position
  cx, cy = new_circle_position

  # Check for the clash and update the score
  scoring_player_id = ''
  if tx == other_tx and ty == other_ty:
    g.board[ty][tx] = "CWTBT"
    g.white_player_score += 1
    scoring_player_id = g.white_player_id
  if cx == other_cx and cy == other_cy:
    g.board[cy][cx] = "CWCBC"
    g.white_player_score += 1
    scoring_player_id = g.white_player_id
  if tx == other_cx and ty == other_cy:
    g.board[ty][tx] = "CWTBC"
    g.black_player_score += 1
    scoring_player_id = g.black_player_id
  if cx == other_tx and cy == other_ty:
    g.board[cy][cx] = "CWCBT"
    g.black_player_score += 1
    scoring_player_id = g.black_player_id

  # Update the board for the current player
  if not g.board[ty][tx]:
    g.board[ty][tx] = current_player_color_code + "T"
  if not g.board[cy][cx]:
    g.board[cy][cx] = current_player_color_code + "C"

  # Was there a clash?
  if scoring_player_id:
    if g.white_player_score == WINNING_SCORE or g.black_player_score == WINNING_SCORE:
      g.game_state = GameState.FINISHED.name
      g.winner_id = scoring_player_id
    else:
      g.game_state = GameState.CLASH.name
  return scoring_player_id


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

  # Check if the player hit the timeout
  last_move = Move.objects.filter(game__exact=g).filter(player_id__exact=user_input.player_id).latest('move_timestamp')
  if last_move and datetime.datetime.now() - last_move.move_timestamp > MAX_TIME_PER_MOVE:
    g.game_state = GameState.FINISHED.name
    g.winner_id = g.black_player_id if color == PlayerColor.WHITE else g.white_player_id
    g.save()
    return GameResponse.from_game(g)

  color_code = "W" if color == PlayerColor.WHITE else "B"
  tx, ty = user_input.new_triangle_position
  cx, cy = user_input.new_circle_position

  # Validate the move.
  if tx == cx and ty == cy:
    return GameResponse.from_game(g).with_error("Invalid position. Same-color figures overlap.")
  if g.board[ty][tx] == "DF" or g.board[cy][cx] == "DF":
    return GameResponse.from_game(g).with_error("Invalid position. Can't move to the destroyed field.")
  # Validate the new position if this is not the first move
  if last_move:
    (old_tx, old_ty) = _find_board_field(g, color_code+"T")
    (old_cx, old_cy) = _find_board_field(g, color_code+"C")
    if abs(old_tx-tx) > 1 or abs(old_cx-cx) > 1 or abs(old_ty-ty) > 1 or abs(old_cy-cy) > 1:
      return GameResponse.from_game(g).with_error("Invalid position. New position is too far.")

  # Update the state & board
  scoring_player_id = ''
  if g.game_state in [GameState.INITIAL_PLACEMENT.name, GameState.GAME_RUNNING.name, GameState.CLASH.name]:
    if user_input.player_id == g.player_1_id:
      g.game_state = GameState.WAITING_PLAYER_TWO_MOVE.name
    else:
      g.game_state = GameState.WAITING_PLAYER_ONE_MOVE.name
    # Update the board. Prefix the content with N as it's not yet fully visible.
    g.board[ty][tx] = "N" + color_code + "T"
    g.board[cy][cx] = "N" + color_code + "C"
  elif g.game_state in [GameState.WAITING_PLAYER_ONE_MOVE.name, GameState.WAITING_PLAYER_TWO_MOVE.name]:
    # Update the state (doesn't have to be final)
    g.game_state = GameState.GAME_RUNNING.name

    # Remove the old positions
    _clear_board_field(g, "WT")
    _clear_board_field(g, "WC")
    _clear_board_field(g, "BT")
    _clear_board_field(g, "BC")
    scoring_player_id = _check_clash_and_update_game(g, color, (tx, ty), (cx, cy))

    # Active the shock field if needed
    if not scoring_player_id and _can_visit_all_figures(g):
      # TODO did we have 8 moves without score change
      # TODO generate shock field and set state
      pass

  g.save()

  # Add it to the move history
  new_move = Move.objects.create(game=g, player_id = user_input.player_id, move_timestamp=datetime.datetime.now(), triangle_position=json.dumps([tx,ty]), circle_position=json.dumps([cx,cy]), scoring_player_id=scoring_player_id)
  new_move.save()

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
