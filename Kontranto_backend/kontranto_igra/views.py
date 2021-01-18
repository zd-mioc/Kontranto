from django.shortcuts import render
from django.http import HttpRequest
from django.http import HttpResponse
from kontranto_igra.game_logic import new_game_f, join_game_f, get_game_state
from kontranto_igra.funkcija_make_move import make_move
import json

def index(request):
    return render(request, "kontranto_igra/homepage.html")

def pravila(request):
    return render(request, "kontranto_igra/pravila.html")

def show_board(request):
    return render(request, "kontranto_igra/board.html")

def new_game(request):
    body_unicode = request.body.decode('utf-8')
    jsonFromBody = json.loads(body_unicode)
    player_1_id = jsonFromBody['player_1_id']
    return HttpResponse(new_game_f(player_1_id), content_type="application/json")

def join_game(request):
    body_unicode = request.body.decode('utf-8')
    jsonFromBody = json.loads(body_unicode)
    game_id = jsonFromBody['game_id']
    player_2_id = jsonFromBody['player_2_id']
    return HttpResponse(join_game_f(game_id, player_2_id), content_type="application/json")

def move(request):
    body_unicode = request.body.decode('utf-8')
    jsonFromBody = json.loads(body_unicode)
    game_id = jsonFromBody['game_id']
    player_id = jsonFromBody['player_id']
    new_triangle_position = jsonFromBody['new_triangle_position']
    new_circle_position = jsonFromBody['new_circle_position']
    return HttpResponse(make_move(game_id, player_id, new_triangle_position, new_circle_position), content_type="application/json")

def board_state(request):
    body_unicode = request.body.decode('utf-8')
    jsonFromBody = json.loads(body_unicode)
    game_id = jsonFromBody['game_id']
    return HttpResponse(get_game_state(game_id), content_type="application/json")
