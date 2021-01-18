from kontranto_igra.models import Game, Move
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
import string
import json

def make_move (game_id, player_id, new_triangle_position, new_circle_position):
    # dohvati zapis iz Game tablice pod ključem "game_id"
    try:
        game=Game.objects.get(game=game_id)
    # greska ako zapis pod game_id ne postoji
    except ObjectDoesNotExist:
        return json.dumps({"status": "Greska: ne postoji igra s tim game_id-em."})
    if game.game_state=="WAITING_FOR_SECOND_PLAYER":
        return json.dumps({"status": "Greska: nedostaje drugi igrac."})
    elif game.game_state=="OVER":
        return json.dumps({"status": "Greska: igra je gotova."})
    player_colour=""
    if player_id==game.white_player_id:
        player_colour="white"
    elif player_id==game.black_player_id:
        player_colour="black"
    else:
        return json.dumps({"status": "player_id nije validan."})
    if player_colour=="white" and game.game_state=="WAITING_FOR_BLACK_PLAYER_MOVE":
        return json.dumps({"status": "vec ste odigrali potez; cekajte potez crnog igraca."})
    elif player_colour=="black" and game.game_state=="WAITING_FOR_WHITE_PLAYER_MOVE":
        return json.dumps({"status": "vec ste odigrali potez; cekajte potez bijelog igraca."})
    
    # greska ako je igrac odigrao potez na ponisteno polje
    # potrebno je prevoditi oznake polja u pozicije u JSON matrici
    triangle_index=ord(new_triangle_position)-97
    if triangle_index>112:
        return json.dumps({"status": "odaberite polje na ploci od a do p."})
    triangle_position=[(triangle_index//4), (triangle_index%4)]
    if "X" in game.board[triangle_position[0]][triangle_position[1]]:
        return json.dumps({"status": "ne mozete se pomaknuti na ponisteno polje."})
    circle_index=ord(new_circle_position)-97
    if circle_index>112:
        return json.dumps({"status": "odaberite polje na ploci od a do p."})
    circle_position=[(circle_index//4), (circle_index%4)]
    if "X" in game.board[circle_position[0]][circle_position[1]]:
        return json.dumps({"status": "ne mozete se pomaknuti na ponisteno polje."})
    if new_triangle_position==new_circle_position:
        return('status: "ne mozete pomaknuti obje figure na isto polje"')

    # greska ako je stanje WAITING_FOR_MOVE a igrac je odigrao na nedohvativo polje
        # dodao sam i za BLACK_PLAYER_MOVE i WHITE_PLAYER_MOVE jer bi trebalo i u tim slucajevima(?)
    max_range=[-1, 0, 1]
    move0=Move.objects.filter(color=player_colour).order_by('-move_timestamp')[0]
    triangle0_index=ord(move0.triangle_position)-97
    triangle0_position=[(triangle0_index//4), (triangle0_index%4)]
    circle0_index=ord(move0.circle_position)-97
    circle0_position=[(circle0_index//4), (circle0_index%4)]
    if game.game_state=="WAITING_FOR_MOVE" or game.game_state=="WAITING_FOR_BLACK_PLAYER_MOVE" or game.game_state=="WAITING_FOR_WHITE_PLAYER_MOVE" and triangle_position[0]-triangle0_position[0] not in max_range:
        return json.dumps({"status": "ne mozete se pomaknuti na nedohvativo polje."})
    elif game.game_state=="WAITING_FOR_MOVE" or game.game_state=="WAITING_FOR_BLACK_PLAYER_MOVE" or game.game_state=="WAITING_FOR_WHITE_PLAYER_MOVE" and triangle_position[1]-triangle0_position[1] not in max_range:
        return json.dumps({"status": "ne mozete se pomaknuti na nedohvativo polje."})
    elif game.game_state=="WAITING_FOR_MOVE" or game.game_state=="WAITING_FOR_BLACK_PLAYER_MOVE" or game.game_state=="WAITING_FOR_WHITE_PLAYER_MOVE" and circle_position[0]-circle0_position[0] not in max_range:
        return json.dumps({"status": "ne mozete se pomaknuti na nedohvativo polje."})
    elif game.game_state=="WAITING_FOR_MOVE" or game.game_state=="WAITING_FOR_BLACK_PLAYER_MOVE" or game.game_state=="WAITING_FOR_WHITE_PLAYER_MOVE" and circle_position[1]-circle0_position[1] not in max_range:
        return json.dumps({"status": "ne mozete se pomaknuti na nedohvativo polje."})

    # trebalo bi uracunati i kraj igre u kojem nije moguce to uciniti pa se figura izbacuje
    # npr postoji jedno available polje i to je zauzeto drugom figurom iste boje
    # ovo bih mogao dodati u igru kad bi osmislili nacin da se izbaci figura iz igre

    move=Move.objects.create(game_id=game.id, color=player_colour, triangle_position=new_triangle_position, circle_position=new_circle_position, move_timestamp=timezone.now())
    game.save()
    
    if game.game_state=="INIT" or game.game_state=="WAITING_FOR_MOVE":
        if player_colour=="white":
            game.game_state="WAITING_FOR_BLACK_PLAYER_MOVE"
        else:
            game.game_state="WAITING_FOR_WHITE_PLAYER_MOVE"
        game.save()
    elif game.game_state=="WAITING_FOR_BLACK_PLAYER_MOVE" or game.game_state=="WAITING_FOR_WHITE_PLAYER_MOVE":
        w_score=game.white_score
        b_score=game.black_score
        # dohvati 2 zadnja poteza iz tablice Move
            # zadnji bi trebao biti nas potez koji je upravo upisan, pa sam dohvatio samo onaj prije njega
        previous_move=Move.objects.filter(game_id=game.id).order_by('-move_timestamp')[1]
        triangle2_index=ord(previous_move.triangle_position)-97
        triangle2_position=[(triangle2_index//4), (triangle2_index%4)]
        circle2_index=ord(previous_move.circle_position)-97
        circle2_position=[(circle2_index//4), (circle2_index%4)]
        # provjeri je li došlo do sudara
        collision="none"
        if move.triangle_position==previous_move.triangle_position:
            collision="triangle_triangle2"
            # ako je, dodijeli bod ovisno o oblicima
            w_score+=1
        elif move.circle_position==previous_move.circle_position:
            collision="circle_circle2"
            w_score+=1
        elif move.triangle_position==previous_move.circle_position:
            collision="triangle_circle2"
            b_score+=1
        elif move.circle_position==previous_move.triangle_position:
            collision="circle_triangle2"
            b_score+=1
        # promijeni pozicije igraca na ploci
        if player_colour=="white":
            if collision=="none":
                game.board[triangle_position[0]][triangle_position[1]]="WT"
                game.board[circle_position[0]][circle_position[1]]="WC"
                game.board[traingle2_position[0]][triangle2_position[1]]="BT"
                game.board[circle2_position[0]][circle2_position[1]]="BC"
            elif collision=="triangle_triangle2":
                game.board[traingle_position[0]][triangle_position[1]]="X,WT,BT"
                game.board[circle_position[0]][circle_position[1]]="WC"
                game.board[circle2_position[0]][circle2_position[1]]="BC"
            elif collision=="circle_circle2":
                game.board[circle_position[0]][circle_position[1]]="X,WC,BC"
                game.board[triangle_position[0]][triangle_position[1]]="WT"
                game.board[traingle2_position[0]][triangle2_position[1]]="BT"
            elif collision=="triangle_circle2":
                game.board[traingle_position[0]][triangle_position[1]]="X,WT,BC"
                game.board[circle_position[0]][circle_position[1]]="WC"
                game.board[traingle2_position[0]][triangle2_position[1]]="BT"
            elif collision=="circle_triangle2":
                game.board[circle_position[0]][circle_position[1]]="X,WC,BT"
                game.board[triangle_position[0]][triangle_position[1]]="WT"
                game.board[circle2_position[0]][circle2_position[1]]="BC"
        else:
            if collision==0:
                game.board[triangle_position[0]][triangle_position[1]]="BT"
                game.board[circle_position[0]][circle_position[1]]="BC"
                game.board[traingle2_position[0]][triangle2_position[1]]="WT"
                game.board[circle2_position[0]][circle2_position[1]]="WC"
            elif collision==1:
                game.board[traingle_position[0]][triangle_position[1]]="X,WT,BT"
                game.board[circle_position[0]][circle_position[1]]="BC"
                game.board[circle2_position[0]][circle2_position[1]]="WC"
            elif collision==2:
                game.board[circle_position[0]][circle_position[1]]="X,WC,BC"
                game.board[triangle_position[0]][triangle_position[1]]="BT"
                game.board[traingle2_position[0]][triangle2_position[1]]="WT"
            elif collision==3:
                game.board[traingle_position[0]][triangle_position[1]]="X,WC,BT"
                game.board[circle_position[0]][circle_position[1]]="BC"
                game.board[traingle2_position[0]][triangle2_position[1]]="WT"
            elif collision==4:
                game.board[circle_position[0]][circle_position[1]]="X,WT,BC"
                game.board[triangle_position[0]][triangle_position[1]]="BT"
                game.board[circle2_position[0]][circle2_position[1]]="WC"
        game.white_score=w_score
        game.black_score=b_score
        game.save()
        if game.white_score==9 or game.black_score==9:
            game.game_state="OVER"
            game.save()
        else:
            game.game_state="WAITING_FOR_MOVE"
            game.save()

    return json.dumps({"status": "OK"})
