from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, request, response
from django.http import HttpResponse
from django.template import loader, RequestContext
from django.middleware.csrf import get_token
from kontranto_igra.game_logic import new_game_f, check_game_new, join_game_f, check_game_join, game_state_f, get_move_f, make_move
import json


def index(request):
    return render(request, "kontranto_igra/homepage.html")

def pravila(request):
    return render(request, "kontranto_igra/pravila.html")

def show_board(request): #tek ako je "status": "OK" kod new/join poziv ide ovdje
    game_id = request.POST.get("game_id")
    player_id = request.POST.get("player_id")
    csrf_token = get_token(request)
    csrf_token_html = '<input type="hidden" name="csrfmiddlewaretoken" value="{}" />'.format(csrf_token)
    if game_id == "to_be_set": #ide na new_game opciju
        template = loader.get_template("kontranto_igra/board.html")
        newgamedata = new_game_f(player_id)
        response_body = template.render({"status" : newgamedata["status"], "game_id": newgamedata["game_id"], "my_id": player_id, "my_color" : newgamedata["my_color"], "csrf" : csrf_token})
        return HttpResponse(response_body)
    else: #ide na join_game opciju
        template = loader.get_template("kontranto_igra/board.html")
        joingamedata = join_game_f(game_id, player_id)
        response_body = template.render({"status" : joingamedata["status"], "game_id": game_id, "my_id": joingamedata["my_id"], "my_color" : joingamedata["my_color"], "csrf": csrf_token})
        # context_instance=RequestContext(request))
        return HttpResponse(response_body)


def new_game(request):
    body_unicode = request.body.decode('utf-8')
    jsonFromBody = json.loads(body_unicode)
    player_id = jsonFromBody['player_id']
    # player_id = request.POST.get("player_id") - ne radi
    new_game_resp = check_game_new(player_id) #prvo radi provjeru
    if new_game_resp["status"] == "OK": #ako je provjera prosla, salje ispravan json
        return HttpResponse(json.dumps(new_game_resp), content_type="application/json")
    else: #inace salje krivi, pa se poziv ne moze poslati
        return HttpResponse(new_game_resp, content_type="application/json")

def join_game(request):
    body_unicode = request.body.decode('utf-8')
    jsonFromBody = json.loads(body_unicode)
    game_id = jsonFromBody['game_id']
    player_id = jsonFromBody['player_id']
    get_game_resp = check_game_join(game_id, player_id) #prvo radi provjeru
    if get_game_resp["status"] == "OK": #ako je provjera prosla, salje ispravan json
        return HttpResponse(json.dumps(get_game_resp), content_type="application/json")
    else: #inace salje krivi, pa se poziv ne moze poslati
        return HttpResponse(get_game_resp, content_type="application/json")

def prijelaz(request):
    return render(request, "kontranto_igra/prijelaz.html")

def move(request):
    body_unicode = request.body.decode('utf-8')
    jsonFromBody = json.loads(body_unicode)
    game_id = jsonFromBody['game_id']
    player_id = jsonFromBody['player_id']
    new_triangle_position = jsonFromBody['new_triangle_position']
    new_circle_position = jsonFromBody['new_circle_position']
    return HttpResponse(make_move(game_id, player_id, new_triangle_position, new_circle_position), content_type="application/json")

def game_state(request): #uzimamo state, id od drugog igraca
    body_unicode = request.body.decode('utf-8')
    jsonFromBody = json.loads(body_unicode)
    game_id = jsonFromBody['game_id']
    my_color = jsonFromBody['my_color']
    return HttpResponse(game_state_f(game_id, my_color), content_type="application/json")

def get_move(request):
    body_unicode = request.body.decode('utf-8')
    jsonFromBody = json.loads(body_unicode)
    game_id = jsonFromBody['game_id']
    opponent_color = jsonFromBody['opponent_color']
    ntp = jsonFromBody['ntp']
    ncp = jsonFromBody['ncp']
    return HttpResponse(get_move_f(game_id, opponent_color, ntp, ncp), content_type="application/json")

def update_info(request):
    return render(request, "kontranto_igra/board.html")
