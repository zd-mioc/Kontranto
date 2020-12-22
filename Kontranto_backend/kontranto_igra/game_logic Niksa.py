from models import Game, Move
from django.core.exceptions import ObjectDoesNotExist
from random import choice
import string

def BlackOrWhite(color): #univerzalna funkcija - može i kod jednog i kod drugog igraca
    if color=='':
        return choice(['black','white'])
    elif color=='white':
        return 'black'
    else:
        return 'white'

def new_game(player_id):
    game_id="".join(choice(string.ascii_letters + string.digits) for i in range(10))
    color_1=BlackOrWhite('')
    if color_1=='black':
        wp=Game.objects.create(white_player_id=player_id)
    else:
        bp=Game.objects.create(black_player_id=player_id)
    g=Game.objects.create(game_id=game_id, game_state="WAITING_FOR_SECOND_PLAYER")
    return game_id, color_1

def join_game(game_id, player_id, color_1):
    try:
        game_id=Game.objects.get(pk=1)
    except ObjectDoesNotExist:
        return "status: 'error'"
    #do kraja ovog try/except rijesena je dodjela boje i unosenje novog igraca (ako je sve regularno)
    try: #isao sam logikom da ne postoji slucaj u kojem nema nijednog igraca vec u igri (tada game_id ne bi postojao, pa bi vec javilo gresku)
        white_player_id=Game.objects.get(pk=2) #pokusava dohvatiti player_id od bijelog
        try: #ako uspije, pokusava i od crnog
            black_player_id=Game.objects.get(pk=3)
        except ObjectDoesNotExist: #bijeli igrac postoji, a crni ne
            bp=Game.objects.create(black_player_id=player_id) #unosi crnog
            color_2='black'
        else: #uspio je dohvatiti i od crnog (i od bijelog) - vec postoje 2 igraca u igri
            return "status: 'error'" #javlja gresku
    except ObjectDoesNotExist: #ne postoji bijeli igrac u igri, znaci da crni postoji
        black_player_id=Game.objects.get(pk=3)
        if black_player_id==player_id: #provjerava zeli li igrac igrati sam sa sobom
            return "status: 'error'" #javlja gresku
        else: #id-evi se ne poklapaju
            wp=Game.objects.create(white_player_id=player_id)
            color_2='white'
    
    #INIT
    return ("status: 'OK'", "color: '{}'".format(color_2))
    
    #color_2=BlackOrWhite(color_1)
    #if color_2=='black':
    #    wp=Game.objects.create(white_player_id=player_id)
    #else:
    #    bp=Game.objects.create(black_player_id=player_id)return ("status: 'OK'", "color: '{}'".format(color_2))

