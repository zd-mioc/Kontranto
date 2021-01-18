from kontranto_igra.models import Game, Move
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
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
        return json.dumps({"status": "Greska: player_id nije validan."})
    game_id = "".join(choice(string.ascii_letters + string.digits) for i in range(10))
    color_1 = BlackOrWhite('')
    if color_1 == 'black':
        g = Game.objects.create(game = game_id, game_state = "WAITING_FOR_SECOND_PLAYER", white_score = 0, black_score = 0, board = [["","","",""], ["","","",""], ["","","",""], ["","","",""]], black_player_id = player_id)
    else:
        g = Game.objects.create(game = game_id, game_state = "WAITING_FOR_SECOND_PLAYER", white_score = 0, black_score = 0, board = [["","","",""], ["","","",""], ["","","",""], ["","","",""]], white_player_id = player_id)
    new_game_f_resp = {
        "game_id": game_id,
        "player_1_color": color_1
    }
    return json.dumps(new_game_f_resp)

def join_game_f(game_id, player_id):
    if player_id == "":
        return json.dumps({"status": "Greska: player_id nije validan."})
    try:
        g = Game.objects.get(game = game_id) #provjerava postoji li igra s tim game_id-em
    except ObjectDoesNotExist:
        return json.dumps({"status": "Greska: ne postoji igra s tim game_id-em."})
    if g.game_state == "INIT": #provjerava je li igra vec pokrenuta
        return json.dumps({"status": "Greska: ta je igra vec pokrenuta."})
    elif g.white_player_id == player_id or g.black_player_id == player_id: #provjerava je li taj igrac vec u igri
        return json.dumps({"status": "Greska: vec ste ukljuceni u tu igru."})
    else: #ako sve stima, provjerava koji igrac (boja) fali
        if g.white_player_id == "":
            g.white_player_id = player_id
            color_2 = "white"
        else:
            g.black_player_id = player_id
            color_2 = "black"
    g.game_state = "INIT"
    g.save() #myb update? - ali s njim javlja gresku
    join_game_f_resp = {
        "status": "OK",
        "player_2_color": color_2
    }
    return json.dumps(join_game_f_resp)

def make_move (game_id, player_id, new_triangle_position, new_circle_position):
    # dohvati zapis iz Game tablice pod ključem "game_id"
    try:
        g=Game.objects.get(game=game_id)
    # greska ako zapis pod game_id ne postoji
    except ObjectDoesNotExist:
        return json.dumps({"status": "Greska: ne postoji igra s tim game_id-em."})
    if g.game_state=="WAITING_FOR_SECOND_PLAYER":
        return json.dumps({"status": "Greska: nedostaje drugi igrac."})
    elif g.game_state=="OVER":
        return json.dumps({"status": "Greska: igra je gotova."})
    if player_id==g.white_player_id:
        player_color="white"
    elif player_id==g.black_player_id:
        player_color="black"
    else:
        return json.dumps({"status": "Greska: player_id nije validan."})
    if player_color=="white" and g.game_state=="WAITING_FOR_BLACK_PLAYER_MOVE":
        return json.dumps({"status": "Greska: vec ste odigrali potez; cekajte potez crnog igraca."})
    elif player_color=="black" and g.game_state=="WAITING_FOR_WHITE_PLAYER_MOVE":
        return json.dumps({"status": "Greska: vec ste odigrali potez; cekajte potez bijelog igraca."})
    
    # greska ako je igrac odigrao potez na ponisteno polje
    # potrebno je prevoditi oznake polja u pozicije u JSON matrici
    triangle_index=ord(new_triangle_position)-97
    if triangle_index>16:
        return json.dumps({"status": "Greska: odaberite polje na ploci od a do p."})
    triangle_position=[(triangle_index//4), (triangle_index%4)]
    if "X" in g.board[triangle_position[0]][triangle_position[1]]:
        return json.dumps({"status": "Greska: ne mozete se pomaknuti na ponisteno polje."})
    circle_index=ord(new_circle_position)-97
    if circle_index>16:
        return json.dumps({"status": "Greska: odaberite polje na ploci od a do p."})
    circle_position=[(circle_index//4), (circle_index%4)]
    if "X" in g.board[circle_position[0]][circle_position[1]]:
        return json.dumps({"status": "Greska: ne mozete se pomaknuti na ponisteno polje."})
    if new_triangle_position==new_circle_position:
        return json.dumps({"status": "Greska: ne mozete pomaknuti obje figure na isto polje"})

    # greska ako je stanje WAITING_FOR_MOVE a igrac je odigrao na nedohvativo polje
        # dodao sam i za BLACK_PLAYER_MOVE i WHITE_PLAYER_MOVE jer bi trebalo i u tim slucajevima(?)
    max_range=[-1, 0, 1]
    move0=Move.objects.filter(color=player_color).order_by('-move_timestamp')[0]
    triangle0_index=ord(move0.triangle_position)-97
    triangle0_position=[(triangle0_index//4), (triangle0_index%4)]
    circle0_index=ord(move0.circle_position)-97
    circle0_position=[(circle0_index//4), (circle0_index%4)]
    if g.game_state=="WAITING_FOR_MOVE" or g.game_state=="WAITING_FOR_BLACK_PLAYER_MOVE" or g.game_state=="WAITING_FOR_WHITE_PLAYER_MOVE" and triangle_position[0]-triangle0_position[0] not in max_range:
        return json.dumps({"status": "Greska: ne mozete se pomaknuti na nedohvativo polje."})
    elif g.game_state=="WAITING_FOR_MOVE" or g.game_state=="WAITING_FOR_BLACK_PLAYER_MOVE" or g.game_state=="WAITING_FOR_WHITE_PLAYER_MOVE" and triangle_position[1]-triangle0_position[1] not in max_range:
        return json.dumps({"status": "Greska: ne mozete se pomaknuti na nedohvativo polje."})
    elif g.game_state=="WAITING_FOR_MOVE" or g.game_state=="WAITING_FOR_BLACK_PLAYER_MOVE" or g.game_state=="WAITING_FOR_WHITE_PLAYER_MOVE" and circle_position[0]-circle0_position[0] not in max_range:
        return json.dumps({"status": "Greska: ne mozete se pomaknuti na nedohvativo polje."})
    elif g.game_state=="WAITING_FOR_MOVE" or g.game_state=="WAITING_FOR_BLACK_PLAYER_MOVE" or g.game_state=="WAITING_FOR_WHITE_PLAYER_MOVE" and circle_position[1]-circle0_position[1] not in max_range:
        return json.dumps({"status": "Greska: ne mozete se pomaknuti na nedohvativo polje."})

    # trebalo bi uracunati i kraj igre u kojem nije moguce to uciniti pa se figura izbacuje
    # npr postoji jedno available polje i to je zauzeto drugom figurom iste boje
    # ovo bih mogao dodati u igru kad bi osmislili nacin da se izbaci figura iz igre

    m=Move.objects.create(game_id=g.id, color=player_color, triangle_position=new_triangle_position, circle_position=new_circle_position, move_timestamp=timezone.now())
    g.save()
    
    if g.game_state=="INIT" or g.game_state=="WAITING_FOR_MOVE":
        if player_color=="white":
            g.game_state="WAITING_FOR_BLACK_PLAYER_MOVE"
        else:
            g.game_state="WAITING_FOR_WHITE_PLAYER_MOVE"
        g.save()
    elif g.game_state=="WAITING_FOR_BLACK_PLAYER_MOVE" or g.game_state=="WAITING_FOR_WHITE_PLAYER_MOVE":
        w_score=g.white_score
        b_score=g.black_score
        # dohvati 2 zadnja poteza iz tablice Move
            # zadnji bi trebao biti nas potez koji je upravo upisan, pa sam dohvatio samo onaj prije njega
        previous_move=Move.objects.filter(game_id=g.id).order_by('-move_timestamp')[1]
        triangle2_index=ord(previous_move.triangle_position)-97
        triangle2_position=[(triangle2_index//4), (triangle2_index%4)]
        circle2_index=ord(previous_move.circle_position)-97
        circle2_position=[(circle2_index//4), (circle2_index%4)]
        # provjeri je li došlo do sudara
        collision="none"
        if m.triangle_position==previous_move.triangle_position:
            collision="triangle_triangle2"
            # ako je, dodijeli bod ovisno o oblicima
            w_score+=1
        elif m.circle_position==previous_move.circle_position:
            collision="circle_circle2"
            w_score+=1
        elif m.triangle_position==previous_move.circle_position:
            collision="triangle_circle2"
            b_score+=1
        elif m.circle_position==previous_move.triangle_position:
            collision="circle_triangle2"
            b_score+=1
        # promijeni pozicije igraca na ploci
        if player_color=="white":
            if collision=="none":
                g.board[triangle_position[0]][triangle_position[1]]="WT"
                g.board[circle_position[0]][circle_position[1]]="WC"
                g.board[triangle2_position[0]][triangle2_position[1]]="BT"
                g.board[circle2_position[0]][circle2_position[1]]="BC"
            elif collision=="triangle_triangle2":
                g.board[triangle_position[0]][triangle_position[1]]="X,WT,BT"
                g.board[circle_position[0]][circle_position[1]]="WC"
                g.board[circle2_position[0]][circle2_position[1]]="BC"
            elif collision=="circle_circle2":
                g.board[circle_position[0]][circle_position[1]]="X,WC,BC"
                g.board[triangle_position[0]][triangle_position[1]]="WT"
                g.board[triangle2_position[0]][triangle2_position[1]]="BT"
            elif collision=="triangle_circle2":
                g.board[triangle_position[0]][triangle_position[1]]="X,WT,BC"
                g.board[circle_position[0]][circle_position[1]]="WC"
                g.board[triangle2_position[0]][triangle2_position[1]]="BT"
            elif collision=="circle_triangle2":
                g.board[circle_position[0]][circle_position[1]]="X,WC,BT"
                g.board[triangle_position[0]][triangle_position[1]]="WT"
                g.board[circle2_position[0]][circle2_position[1]]="BC"
        else:
            if collision==0:
                g.board[triangle_position[0]][triangle_position[1]]="BT"
                g.board[circle_position[0]][circle_position[1]]="BC"
                g.board[triangle2_position[0]][triangle2_position[1]]="WT"
                g.board[circle2_position[0]][circle2_position[1]]="WC"
            elif collision==1:
                g.board[triangle_position[0]][triangle_position[1]]="X,WT,BT"
                g.board[circle_position[0]][circle_position[1]]="BC"
                g.board[circle2_position[0]][circle2_position[1]]="WC"
            elif collision==2:
                g.board[circle_position[0]][circle_position[1]]="X,WC,BC"
                g.board[triangle_position[0]][triangle_position[1]]="BT"
                g.board[triangle2_position[0]][triangle2_position[1]]="WT"
            elif collision==3:
                g.board[triangle_position[0]][triangle_position[1]]="X,WC,BT"
                g.board[circle_position[0]][circle_position[1]]="BC"
                g.board[triangle2_position[0]][triangle2_position[1]]="WT"
            elif collision==4:
                g.board[circle_position[0]][circle_position[1]]="X,WT,BC"
                g.board[triangle_position[0]][triangle_position[1]]="BT"
                g.board[circle2_position[0]][circle2_position[1]]="WC"
        g.white_score=w_score
        g.black_score=b_score
        g.save()
        if g.white_score==9 or g.black_score==9:
            g.game_state="OVER"
            g.save()
        else:
            g.game_state="WAITING_FOR_MOVE"
            g.save()

    return json.dumps({"status": "OK"})

def get_game_state(game_id):
    try:
        g = Game.objects.get(game = game_id)
        m = Move.objects.filter(game_id = g.id).order_by('-move_timestamp')[0]
        get_game_state_resp = {
            "last_move_timestamp": m.move_timestamp,
            "board": g.board,
            "white_score": g.white_score,
            "black_score": g.black_score,
            "game_state": g.game_state
        }
        return json.dumps(get_game_state_resp, cls=DjangoJSONEncoder) #zbog timestamp-a
    except ObjectDoesNotExist:
        return json.dumps({"status": "Greska: ne postoji igra s tim game_id-em."})