from django.shortcuts import render
from django.http import HttpRequest
from django.http import HttpResponse
from .services import funkcije
import json

def index(request):
    return render(request, "kontranto_igra/homepage.html")

def pravila(request):
    return render(request, "kontranto_igra/pravila.html")

def new_game(request):
    body_unicode = request.body.decode('utf-8')
    jsonFromBody = json.loads(body_unicode)
    player1Id = jsonFromBody['player1_id'] 
    return HttpResponse('{"game_id": "'+funkcije.random_game_id()+'", "player1_color": "'+funkcije.BlackOrWhite('')+'"}', content_type="application/json")

def join_game(request): #prima player1_color da zna vratiti pravu boju
    body_unicode = request.body.decode('utf-8')
    jsonFromBody = json.loads(body_unicode)
    gameId = jsonFromBody['game_id']
    player2Id = jsonFromBody['player2_id']
    player1_color = jsonFromBody['player1_color']
    return HttpResponse('{"status": "'+funkcije.status(gameId)+'", "player2_color": "'+funkcije.BlackOrWhite(player1_color)+'"}', content_type="application/json")

def move(request):
    body_unicode = request.body.decode('utf-8')
    jsonFromBody = json.loads(body_unicode)
    gameId = jsonFromBody['game_id']
    playerId = jsonFromBody['player_id']
    ntp = jsonFromBody['new_triangle_position']
    ncp = jsonFromBody['new_circle_position']
    return HttpResponse('{"status": "OK"}', content_type="application/json")

def board_state(request):
    body_unicode = request.body.decode('utf-8')
    jsonFromBody = json.loads(body_unicode)
    gameId = jsonFromBody['game_id']
    return HttpResponse('{"last_move_timestamp": "<vrijeme_posljednjeg_odigranog_poteza>", "board": "<serijalizirano_stanje_ploce>", "white_score": "<bodovi_bijelog>", "black_score": "<bodovi_crnog>"}', content_type="application/json")
