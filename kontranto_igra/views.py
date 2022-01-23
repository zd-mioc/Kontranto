import json
import logging
import dataclasses

from typing import Tuple, List

from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpRequest, request, response
from django.template import loader, RequestContext
from django.middleware import csrf

from kontranto_igra import game_logic, forms

logger = logging.getLogger(__name__)


def index(request):
  """Renders the index page."""
  new_game_form = forms.NewGameForm()
  join_game_form = forms.JoinGameForm()
  return render(request, "kontranto_igra/index.html", {'new_game_form': new_game_form, 'join_game_form': join_game_form})


def game_rules(request):
  """Renders the game rules page."""
  return render(request, "kontranto_igra/pravila.html")


def new_game(request):
  """Creates a new game and renders the board."""
  if request.method == 'POST':
    new_game_form = forms.NewGameForm(request.POST)
    if new_game_form.is_valid():
      # TODO: get the player_id from the auth context
      player_id = new_game_form.cleaned_data['player_id']
      gr = game_logic.create_game(player_id)
      return redirect("show_board", game_id=gr.game_id, player_id=player_id)
  # TODO: handle the error
  return redirect("")


def join_game(request):
  """Joins a new player to the game."""
  if request.method == 'POST':
    join_game_form = forms.JoinGameForm(request.POST)
    if join_game_form.is_valid():
      # TODO: get the player_id from the auth context
      player_id = join_game_form.cleaned_data['player_id']
      gr = game_logic.join_game(player_id, join_game_form.cleaned_data['game_id'])
      return redirect("show_board", game_id=gr.game_id, player_id=player_id)
  # TODO: handle the error
  return redirect("")


def show_board(request, game_id, player_id):
  """Renders the Kontranto board for the given game."""
  # TODO: get the player_id from the auth context
  gr = game_logic.get_game_state(player_id, game_id)
  template = loader.get_template("kontranto_igra/board.html")
  response_body = template.render({"status" : gr.game_state, "game_id": gr.game_id, "my_id": player_id, "my_color" : gr.current_player_color, "csrf": csrf.get_token(request)})
  # TODO: properly pass the context
  # context_instance=RequestContext(request))
  return HttpResponse(response_body)


def _to_json_response(response: game_logic.GameResponse) -> HttpResponse:
  """Returns the input dict wrapped as JSON in the HTTP response."""
  return HttpResponse(json.dumps(dataclasses.asdict(response)), content_type="application/json")


def game_state(request, game_id, player_id):
  """Returns the current state of the game (e.g. the board & the score)."""
  gr = game_logic.get_game_state(player_id, game_id)
  return _to_json_response(gr)


def _get_user_input(request_body: bytes) -> Tuple[game_logic.UserInput, HttpResponse]:
  """Parses the request body and returns (UserInput, ErrorResponse).

  In case of invalid user input, error HTTP Response is returned.
  """
  def _error_response(error_message: str):
    return (None, _to_json_response(game_logic.GameResponse.from_error(error_message)))

  try:
    request_data = json.loads(request_body.decode('utf-8'))
  except Exception as e:
    logger.debug("Failed to parse JSON from: {request_body}")
    return _error_response("Invalid request!")

  # TODO: replace player_id with the player login
  missing_req_fields = []
  required_fields = ["player_id", "game_id"]
  for f in required_fields:
    if f not in game_logic.UserInput.__annotations__.keys():
      logger.error("UserInput doesn't contain field '{f}''.")
      return _error_response("Internal error")
    if f not in request_data:
      missing_req_fields.append(f)
  if missing_req_fields:
    return _error_response("Missing required fields: %s" % ", ".join(missing_req_fields))
  return (game_logic.UserInput.from_dict(request_data), None)


def move(request):
  """Handles player's move."""
  user_input, err = _get_user_input(request.body)
  if err:
      return err
  gr = game_logic.handle_game_action(user_input)
  return _to_json_response(gr)
