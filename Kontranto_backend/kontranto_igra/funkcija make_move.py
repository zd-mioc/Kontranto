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
        return json.dumps({"status": "error"})
        break
    if game.game_state=="WAITING_FOR_SECOND_PLAYER" or game.game_state=="OVER":
        return json.dumps({"status": "error"})
        break
    player_colour=""
    if player_id==game.white_player_id:
        player_colour="white"
    elif player_id==game.black_player_id:
        player_colour="black"
    else:
        return json.dumps({"status": "error"})
        break
    if player_colour=="white" and game.game_state=="WAITING_FOR_BLACK_PLAYER_MOVE":
        return json.dumps({"status": "error"})
        break
    elif player_colour=="black" and game.game_state=="WAITING_FOR_WHITE_PLAYER_MOVE":
        return json.dumps({"status": "error"})
        break
    
    # greska ako je igrac odigrao potez na ponisteno polje
    # potrebno je prevoditi oznake polja u pozicije u JSON matrici
    if new_triangle_position=="a":
        triangle_position=[0, 0]
    elif new_triangle_position=="b":
        triangle_position=[0, 1]
    elif new_triangle_position=="c":
        triangle_position=[0, 2]
    elif new_triangle_position=="d":
        triangle_position=[0, 3]
    elif new_triangle_position=="e":
        triangle_position=[1, 0]
    elif new_triangle_position=="f":
        triangle_position=[1, 1]
    elif new_triangle_position=="g":
        triangle_position=[1, 2]
    elif new_triangle_position=="h":
        triangle_position=[1, 3]
    elif new_triangle_position=="i":
        triangle_position=[2, 0]
    elif new_triangle_position=="j":
        triangle_position=[2, 1]
    elif new_triangle_position=="k":
        triangle_position=[2, 2]
    elif new_triangle_position=="l":
        triangle_position=[2, 3]
    elif new_triangle_position=="m":
        triangle_position=[3, 0]
    elif new_triangle_position=="n":
        triangle_position=[3, 1]
    elif new_triangle_position=="o":
        triangle_position=[3, 2]
    elif new_triangle_position=="p":
        triangle_position=[3, 3]
    else:
        return json.dumps({"status": "error"})
        break
    if game.board[triangle_position[0]][triangle_position[1]]=="X" or game.board[triangle_position[0]][triangle_position[1]]=="X,WC" or game.board[triangle_position[0]][triangle_position[1]]=="X,WT" or game.board[triangle_position[0]][triangle_position[1]]=="X,BC" or game.board[triangle_position[0]][triangle_position[1]]=="X,BC":
        return json.dumps({"status": "error"})
        break
    if new_circle_position=="a":
        circle_position=[0, 0]
    elif new_circle_position=="b":
        circle_position=[0, 1]
    elif new_circle_position=="c":
        circle_position=[0, 2]
    elif new_circle_position=="d":
        circle_position=[0, 3]
    elif new_circle_position=="e":
        circle_position=[1, 0]
    elif new_circle_position=="f":
        circle_position=[1, 1]
    elif new_circle_position=="g":
        circle_position=[1, 2]
    elif new_circle_position=="h":
        circle_position=[1, 3]
    elif new_circle_position=="i":
        circle_position=[2, 0]
    elif new_circle_position=="j":
        circle_position=[2, 1]
    elif new_circle_position=="k":
        circle_position=[2, 2]
    elif new_circle_position=="l":
        circle_position=[2, 3]
    elif new_circle_position=="m":
        circle_position=[3, 0]
    elif new_circle_position=="n":
        circle_position=[3, 1]
    elif new_circle_position=="o":
        circle_position=[3, 2]
    elif new_circle_position=="p":
        circle_position=[3, 3]
    else:
        return json.dumps({"status": "error"})
        break
    if game.board[circle_position[0]][circle_position[1]]=="X" or game.board[circle_position[0]][circle_position[1]]=="X,WC" or game.board[circle_position[0]][circle_position[1]]=="X,WT" or game.board[circle_position[0]][circle_position[1]]=="X,BC" or game.board[circle_position[0]][circle_position[1]]=="X,BC":
        return json.dumps({"status": "error"})
        break
    if new_triangle_position==new_circle_position:
        return('status: "error"')
        break

    # greska ako je stanje WAITING_FOR_MOVE a igrac je odigrao na nedohvativo polje
        # dodao sam i za BLACK_PLAYER_MOVE i WHITE_PLAYER_MOVE jer bi trebalo i u tim slucajevima(?)
    max_range=[-1, 0, 1]
    move0=Move.objects.filter(color=player_colour).order_by('-move_timestamp')[0]
    if move0.triangle_position=="a":
        triangle0_position=[0, 0]
    elif move0.triangle_position=="b":
        triangle0_position=[0, 1]
    elif move0.triangle_position=="c":
        triangle0_position=[0, 2]
    elif move0.triangle_position=="d":
        triangle0_position=[0, 3]
    elif move0.triangle_position=="e":
        triangle0_position=[1, 0]
    elif move0.triangle_position=="f":
        triangle0_position=[1, 1]
    elif move0.triangle_position=="g":
        triangle0_position=[1, 2]
    elif move0.triangle_position=="h":
        triangle0_position=[1, 3]
    elif move0.triangle_position=="i":
        triangle0_position=[2, 0]
    elif move0.triangle_position=="j":
        triangle0_position=[2, 1]
    elif move0.triangle_position=="k":
        triangle0_position=[2, 2]
    elif move0.triangle_position=="l":
        triangle0_position=[2, 3]
    elif move0.triangle_position=="m":
        triangle0_position=[3, 0]
    elif move0.triangle_position=="n":
        triangle0_position=[3, 1]
    elif move0.triangle_position=="o":
        triangle0_position=[3, 2]
    elif move0.triangle_position=="p":
        triangle0_position=[3, 3]
    if move0.circle_position=="a":
        circle0_position=[0, 0]
    elif move0.circle_position=="b":
        circle0_position=[0, 1]
    elif move0.circle_position=="c":
        circle0_position=[0, 2]
    elif move0.circle_position=="d":
        circle0_position=[0, 3]
    elif move0.circle_position=="e":
        circle0_position=[1, 0]
    elif move0.circle_position=="f":
        circle0_position=[1, 1]
    elif move0.circle_position=="g":
        circle0_position=[1, 2]
    elif move0.circle_position=="h":
        circle0_position=[1, 3]
    elif move0.circle_position=="i":
        circle0_position=[2, 0]
    elif move0.circle_position=="j":
        circle0_position=[2, 1]
    elif move0.circle_position=="k":
        circle0_position=[2, 2]
    elif move0.circle_position=="l":
        circle0_position=[2, 3]
    elif move0.circle_position=="m":
        circle0_position=[3, 0]
    elif move0.circle_position=="n":
        circle0_position=[3, 1]
    elif move0.circle_position=="o":
        circle0_position=[3, 2]
    elif move0.circle_position=="p":
        circle0_position=[3, 3]
    if game.game_state=="WAITING_FOR_MOVE" or game.game_state=="WAITING_FOR_BLACK_PLAYER_MOVE" or game.game_state=="WAITING_FOR_WHITE_PLAYER_MOVE" and triangle_position[0]-triangle0_position[0] not in max_range:
        return json.dumps({"status": "error"})
        break
    elif game.game_state=="WAITING_FOR_MOVE" or game.game_state=="WAITING_FOR_BLACK_PLAYER_MOVE" or game.game_state=="WAITING_FOR_WHITE_PLAYER_MOVE" and triangle_position[1]-triangle0_position[1] not in max_range:
        return json.dumps({"status": "error"})
        break
    elif game.game_state=="WAITING_FOR_MOVE" or game.game_state=="WAITING_FOR_BLACK_PLAYER_MOVE" or game.game_state=="WAITING_FOR_WHITE_PLAYER_MOVE" and circle_position[0]-circle0_position[0] not in max_range:
        return json.dumps({"status": "error"})
        break
    elif game.game_state=="WAITING_FOR_MOVE" or game.game_state=="WAITING_FOR_BLACK_PLAYER_MOVE" or game.game_state=="WAITING_FOR_WHITE_PLAYER_MOVE" and circle_position[1]-circle0_position[1] not in max_range:
        return json.dumps({"status": "error"})
        break

    # greska ako je prethodni potez doveo do sudara, a igrac nije maknuo figuru
    # nije li ovo nepotrebno, obzirom da je to polje sada postalo ponistenim poljem, dakle kako bi igrac ostao na njemu morao bi odigrati potez na ponisteno polje, sto je pokriveno gore?
        # s tim da bi trebalo uracunati i kraj igre u kojem nije moguce to uciniti pa se figura izbacuje
        # npr postoji jedno available polje i to je zauzeto drugom figurom iste boje
        # ovo bih mogao dodati u igru kad bi osmislili nacin da se izbaci figura iz igre

    # dodaj zapis u tablicu Move
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
        if previous_move.triangle_position=="a":
            triangle2_position=[0, 0]
        elif previous_move.triangle_position=="b":
            triangle2_position=[0, 1]
        elif previous_move.triangle_position=="c":
            triangle2_position=[0, 2]
        elif previous_move.triangle_position=="d":
            triangle2_position=[0, 3]
        elif previous_move.triangle_position=="e":
            triangle2_position=[1, 0]
        elif previous_move.triangle_position=="f":
            triangle2_position=[1, 1]
        elif previous_move.triangle_position=="g":
            triangle2_position=[1, 2]
        elif previous_move.triangle_position=="h":
            triangle2_position=[1, 3]
        elif previous_move.triangle_position=="i":
            triangle2_position=[2, 0]
        elif previous_move.triangle_position=="j":
            triangle2_position=[2, 1]
        elif previous_move.triangle_position=="k":
            triangle2_position=[2, 2]
        elif previous_move.triangle_position=="l":
            triangle2_position=[2, 3]
        elif previous_move.triangle_position=="m":
            triangle2_position=[3, 0]
        elif previous_move.triangle_position=="n":
            triangle2_position=[3, 1]
        elif previous_move.triangle_position=="o":
            triangle2_position=[3, 2]
        elif previous_move.triangle_position=="p":
            triangle2_position=[3, 3]
        if previous_move.circle_position=="a":
            circle2_position=[0, 0]
        elif previous_move.circle_position=="b":
            circle2_position=[0, 1]
        elif previous_move.circle_position=="c":
            circle2_position=[0, 2]
        elif previous_move.circle_position=="d":
            circle2_position=[0, 3]
        elif previous_move.circle_position=="e":
            circle2_position=[1, 0]
        elif previous_move.circle_position=="f":
            circle2_position=[1, 1]
        elif previous_move.circle_position=="g":
            circle2_position=[1, 2]
        elif previous_move.circle_position=="h":
            circle2_position=[1, 3]
        elif previous_move.circle_position=="i":
            circle2_position=[2, 0]
        elif previous_move.circle_position=="j":
            circle2_position=[2, 1]
        elif previous_move.circle_position=="k":
            circle2_position=[2, 2]
        elif previous_move.circle_position=="l":
            circle2_position=[2, 3]
        elif previous_move.circle_position=="m":
            circle2_position=[3, 0]
        elif previous_move.circle_position=="n":
            circle2_position=[3, 1]
        elif previous_move.circle_position=="o":
            circle2_position=[3, 2]
        elif previous_move.circle_position=="p":
            circle2_position=[3, 3]
        # provjeri je li došlo do sudara
        collision=0
        if move.triangle_position==previous_move.triangle_position:
            collision=1
            # ako je, dodijeli bod ovisno o oblicima
            w_score+=1
            # ako je, oznaci polje kao ponisteno
                # napravljeno pri promjeni pozicija igraca na ploci
        elif move.circle_position==previous_move.circle_position:
            collision=2
            w_score+=1
        elif move.triangle_position==previous_move.circle_position:
            collision=3
            b_score+=1
        elif move.circle_position==previous_move.triangle_position:
            collision=4
            b_score+=1
        # promijeni pozicije igraca na ploci
        if player_colour=="white":
            if collision==0:
                game.board[triangle_position[0]][triangle_position[1]]="WT"
                game.board[circle_position[0]][circle_position[1]]="WC"
                game.board[traingle2_position[0]][triangle2_position[1]]="BT"
                game.board[circle2_position[0]][circle2_position[1]]="BC"
            elif collision==1:
                game.board[traingle_position[0]][triangle_position[1]]="X,WT,BT"
                game.board[circle_position[0]][circle_position[1]]="WC"
                game.board[circle2_position[0]][circle2_position[1]]="BC"
            elif collision==2:
                game.board[circle_position[0]][circle_position[1]]="X,WC,BC"
                game.board[triangle_position[0]][triangle_position[1]]="WT"
                game.board[traingle2_position[0]][triangle2_position[1]]="BT"
            elif collision==3:
                game.board[traingle_position[0]][triangle_position[1]]="X,WT,BC"
                game.board[circle_position[0]][circle_position[1]]="WC"
                game.board[traingle2_position[0]][triangle2_position[1]]="BT"
            elif collision==4:
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
