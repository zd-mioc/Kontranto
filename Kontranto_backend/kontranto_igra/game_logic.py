from kontranto_igra.models import Game, Move
from django.core.exceptions import ObjectDoesNotExist
from random import choice
import string
import json

def BlackOrWhite(color): #univerzalna funkcija - moze i kod jednog i kod drugog igraca
    if color == '':
        return choice(['black','white'])
    elif color == 'white':
        return 'black'
    else:
        return 'white'

def new_game_f(player_id):
    if player_id == "":
        return json.dumps({"status": "Greška: player_id nije validan."})
    game_id = "".join(choice(string.ascii_letters + string.digits) for i in range(10))
    g = Game.objects.create(game_id = game_id, game_state = "WAITING_FOR_SECOND_PLAYER")
    color_1 = BlackOrWhite('')
    if color_1 == 'black':
        g.black_player_id = player_id  
    else:
        g.white_player_id = player_id
    g.save()
    new_game_f_resp = {
        "game_id": game_id,
        "player_1_color": color_1
    }
    return json.dumps(new_game_f_resp)

def join_game_f(game_id, player_id):
    if player_id == "":
        return json.dumps({"status": "Greška: player_id nije validan."})
    try:
        g = Game.objects.get(game_id = game_id) #provjerava postoji li igra s tim game_id-em
    except ObjectDoesNotExist:
        return json.dumps({"status": "Greška: ne postoji igra s tim game_id-em."})
    if g.game_state == "INIT": #provjerava je li igra vec pokrenuta
        return json.dumps({"status": "Greška: ta je igra već pokrenuta."})
    elif g.white_player_id == player_id or g.black_player_id == player_id: #provjerava je li taj igrac vec u igri
        return json.dumps({"status": "Greška: već ste uključeni u tu igru."})
    else: #ako sve stima, provjerava koji igrac (boja) fali
        if g.white_player_id == "":
            g.white_player_id = player_id
            color_2 = "white"
        else:
            g.black_player_id = player_id
            color_2 = "black"
    g.game_state = "INIT"
    g.update() #myb save?
    join_game_f_resp = {
        "status": "OK",
        "player_2_color": color_2
    }
    return json.dumps(join_game_f_resp) 

def get_game_state(game_id):
    try:
        g = Game.objects.get(game_id = game_id)
        m = Move.objects.filter(game_id = game_id).order_by('-move_timestamp')[0]
        get_game_state_resp = {
            "last_move_timestamp": m.last_move_timestamp,
            "board": g.board,
            "white_score": g.white_score,
            "black_score": g.black_score,
            "game_state": g.game_state
        }
        return json.dumps(get_game_state_resp)
    except ObjectDoesNotExist:
        return json.dumps({"status": "Greška: ne postoji igra s tim game_id-em."})