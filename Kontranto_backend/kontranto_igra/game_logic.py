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

# funkcija rotate potrebna unutar funkcije make_move pri provjeri razdvojene ploce
def rotate(l):
    for i in range(int(len(l)/2)):
        if l[2*i]==1 and l[2*i+1]==1:
            l[2*i+1]=2
        elif l[2*i]==1 and l[2*i+1]==2:
            l[2*i]=2
        elif l[2*i]==2 and l[2*i+1]==2:
            l[2*i+1]=1
        elif l[2*i]==2 and l[2*i+1]==1:
            l[2*i]=1
        else:
            x=l[2*i]
            y=l[2*i+1]
            x=3-x
            l[2*i]=y
            l[2*i+1]=x

def make_move (game_id, player_id, new_triangle_position, new_circle_position):
    try:
        g=Game.objects.get(game=game_id)
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

    triangle_position=new_triangle_position
    circle_position=new_circle_position
    if "X" in g.board[triangle_position[0]][triangle_position[1]]:
        return json.dumps({"status": "Greska: ne mozete se pomaknuti na ponisteno polje."})
    if "X" in g.board[circle_position[0]][circle_position[1]]:
        return json.dumps({"status": "Greska: ne mozete se pomaknuti na ponisteno polje."})
    if new_triangle_position==new_circle_position:
        return json.dumps({"status": "Greska: ne mozete pomaknuti obje figure na isto polje"})

    # greska ako je igrac odigrao na nedohvativo polje
        # treba prvo provjeriti radi li se o pocetku igre jer su tada sva polja dostupna
        # provjeravamo imaju li zadnja dva poteza odgovarajuci game_id, odnosno ima li prethodnih poteza u ovoj igri; ako ne onda je nova igra
    m0=Move.objects.order_by('-move_timestamp')[0]
    m00=Move.objects.order_by('-move_timestamp')[1]
    if m0.game_id==g.id and m00.game_id==g.id:
        max_range=[-1, 0, 1]
        move0=Move.objects.filter(color=player_color).order_by('-move_timestamp')[0]    # dohvacamo prijasnji potez igraca ove boje kako bismo mu utvrdili trenutnu lokaciju
        triangle0_position=move0.triangle_position
        circle0_position=move0.circle_position
        if triangle_position[0]-triangle0_position[0] not in max_range:
            return json.dumps({"status": "Greska: ne mozete se pomaknuti na nedohvativo polje."})
        elif triangle_position[1]-triangle0_position[1] not in max_range:
            return json.dumps({"status": "Greska: ne mozete se pomaknuti na nedohvativo polje."})
        elif circle_position[0]-circle0_position[0] not in max_range:
            return json.dumps({"status": "Greska: ne mozete se pomaknuti na nedohvativo polje."})
        elif circle_position[1]-circle0_position[1] not in max_range:
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
        # dohvacamo 2 zadnja poteza iz tablice Move
            # zadnji bi trebao biti nas potez koji je upravo upisan, pa dohvacamo samo onaj prije njega
        previous_move=Move.objects.filter(game_id=g.id).order_by('-move_timestamp')[1]
        triangle2_position=previous_move.triangle_position
        circle2_position=previous_move.circle_position
        # provjeravamo je li doslo do sudara
        collision="none"
        if m.triangle_position==previous_move.triangle_position and m.circle_position==previous_move.circle_position:
            collision="double_collision_same"
            w_score+=2
        elif m.triangle_position==previous_move.circle_position and m.circle_position==previous_move.triangle_position:
            collision="double_collision_different"
            b_score+=2
        elif m.triangle_position==previous_move.triangle_position:
            collision="triangle_triangle2"
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
        # mijenjamo pozicije igraca na ploci
        m0=Move.objects.order_by('-move_timestamp')[2]
        m00=Move.objects.order_by('-move_timestamp')[3]
        triangle0_position=m0.triangle_position
        circle0_position=m0.circle_position
        triangle00_position=m00.triangle_position
        circle00_position=m00.circle_position
        if "WX" in g.board[triangle0_position[0]][triangle0_position[1]]:
            g.board[triangle0_position[0]][triangle0_position[1]]="WX"
        elif "BX" in g.board[triangle0_position[0]][triangle0_position[1]]:
            g.board[triangle0_position[0]][triangle0_position[1]]="BX"
        else:
            g.board[triangle0_position[0]][triangle0_position[1]]=""
        if "WX" in g.board[circle0_position[0]][circle0_position[1]]:
            g.board[circle0_position[0]][circle0_position[1]]="WX"
        elif "BX" in g.board[circle0_position[0]][circle0_position[1]]:
            g.board[circle0_position[0]][circle0_position[1]]="BX"
        else:
            g.board[circle0_position[0]][circle0_position[1]]=""
        if "WX" in g.board[triangle00_position[0]][triangle00_position[1]]:
            g.board[triangle00_position[0]][triangle00_position[1]]="WX"
        elif "BX" in g.board[triangle00_position[0]][triangle00_position[1]]:
            g.board[triangle00_position[0]][triangle00_position[1]]="BX"
        else:
            g.board[triangle00_position[0]][triangle00_position[1]]=""
        if "WX" in g.board[circle00_position[0]][circle00_position[1]]:
            g.board[circle00_position[0]][circle00_position[1]]="WX"
        elif "BX" in g.board[circle00_position[0]][circle00_position[1]]:
            g.board[circle00_position[0]][circle00_position[1]]="BX"
        else:
            g.board[circle00_position[0]][circle00_position[1]]=""
        
        if collision=="double_collision_same":
            g.board[triangle_position[0]][triangle_position[1]]="WX,WT,BT"
            g.board[circle_position[0]][circle_position[1]]="WX,WC,BC"
        elif collision=="double_collision_different":
            g.board[triangle_position[0]][triangle_position[1]]="BX,WT,BC"
            g.board[circle_position[0]][circle_position[1]]="BX,WC,BT"
        elif player_color=="white":
            if collision=="none":
                g.board[triangle_position[0]][triangle_position[1]]="WT"
                g.board[circle_position[0]][circle_position[1]]="WC"
                g.board[triangle2_position[0]][triangle2_position[1]]="BT"
                g.board[circle2_position[0]][circle2_position[1]]="BC"
            elif collision=="triangle_triangle2":
                g.board[triangle_position[0]][triangle_position[1]]="WX,WT,BT"
                g.board[circle_position[0]][circle_position[1]]="WC"
                g.board[circle2_position[0]][circle2_position[1]]="BC"
            elif collision=="circle_circle2":
                g.board[circle_position[0]][circle_position[1]]="WX,WC,BC"
                g.board[triangle_position[0]][triangle_position[1]]="WT"
                g.board[triangle2_position[0]][triangle2_position[1]]="BT"
            elif collision=="triangle_circle2":
                g.board[triangle_position[0]][triangle_position[1]]="BX,WT,BC"
                g.board[circle_position[0]][circle_position[1]]="WC"
                g.board[triangle2_position[0]][triangle2_position[1]]="BT"
            elif collision=="circle_triangle2":
                g.board[circle_position[0]][circle_position[1]]="BX,WC,BT"
                g.board[triangle_position[0]][triangle_position[1]]="WT"
                g.board[circle2_position[0]][circle2_position[1]]="BC"
        else:
            if collision=="none":
                g.board[triangle_position[0]][triangle_position[1]]="BT"
                g.board[circle_position[0]][circle_position[1]]="BC"
                g.board[triangle2_position[0]][triangle2_position[1]]="WT"
                g.board[circle2_position[0]][circle2_position[1]]="WC"
            elif collision=="triangle_triangle2":
                g.board[triangle_position[0]][triangle_position[1]]="WX,WT,BT"
                g.board[circle_position[0]][circle_position[1]]="BC"
                g.board[circle2_position[0]][circle2_position[1]]="WC"
            elif collision=="circle_circle2":
                g.board[circle_position[0]][circle_position[1]]="WX,WC,BC"
                g.board[triangle_position[0]][triangle_position[1]]="BT"
                g.board[triangle2_position[0]][triangle2_position[1]]="WT"
            elif collision=="triangle_circle2":
                g.board[triangle_position[0]][triangle_position[1]]="BX,WC,BT"
                g.board[circle_position[0]][circle_position[1]]="BC"
                g.board[triangle2_position[0]][triangle2_position[1]]="WT"
            elif collision=="circle_triangle2":
                g.board[circle_position[0]][circle_position[1]]="BX,WT,BC"
                g.board[triangle_position[0]][triangle_position[1]]="BT"
                g.board[circle2_position[0]][circle2_position[1]]="WC"

        # provjera ponovljenih pozicija
        m0=Move.objects.order_by('-move_timestamp')[1]
        m00=Move.objects.order_by('-move_timestamp')[2]
        if m0.game_id!=g.id or m00.game_id!=g.id:
            null_fields=[]
        else:
            null_fields=m0.null_fields
            if collision=="double_collision_same" or collision=="double_collision_different":
                null_fields+=[chr(97+triangle_position[0]*4+triangle_position[1])]
                null_fields+=[chr(97+circle_position[0]*4+circle_position[1])]
            elif collision=="triangle_triangle2" or collision=="triangle_circle2":
                null_fields+=[chr(97+triangle_position[0]*4+triangle_position[1])]
            elif collision=="circle_circle2" or collision=="circle_triangle2":
                null_fields+=[chr(97+circle_position[0]*4+circle_position[1])]
            elif collision=="none" and Move.objects.order_by('-move_timestamp')[3].null_fields==Move.objects.order_by('-move_timestamp')[2].null_fields:
                i=0
                while Move.objects.order_by('-move_timestamp')[i].null_fields==Move.objects.order_by('-move_timestamp')[0].null_fields:
                    if i!=1 and i%2==1:
                        move_i_a=Move.objects.order_by('-move_timestamp')[i]
                        move_i_b=Move.objects.order_by('-move_timestamp')[i-1]
                        move_a=Move.objects.filter(color=move_i_a.color).order_by('-move_timestamp')[0]
                        move_b=Move.objects.filter(color=move_i_b.color).order_by('-move_timestamp')[0]
                        if move_i_a.triangle_position==move_a.triangle_position and move_i_a.circle_position==move_a.circle_position and move_i_b.triangle_position==move_b.triangle_position and move_i_b.circle_position==move_b.circle_position:
                        # triba sad izbrisati te poteze nekako i uciniti da i drugi igrac igra ponovno
                            g.game_state="WAITING_FOR_MOVE"
                            return json.dumps({"status": "Greska: prijasnja pozicija ne smije biti ponovljena; oba igraca igraju ponovno"})
                    i+=1
        m.null_fields=null_fields
        
        g.white_score=w_score
        g.black_score=b_score
        g.save()
        if g.white_score==9 or g.black_score==9:
            g.game_state="OVER"
            g.save()
        
        # provjera razdvojene ploce - bar jedno sredisnje polje mora biti ponisteno kako bi moglo doci do razdvajanja ploce
        elif g.board[1][1]==("WX" or "BX") or g.board[1][2]==("WX" or "BX") or g.board[2][1]==("WX" or "BX") or g.board[2][2]==("WX" or "BX"):
            # provjerava koliko je sredisnjih polja ponisteno; prema tome razvrstavamo razlicite mogucnosti
            n=0
            if g.board[1][1]==("WX" or "BX"):
                n+=1
            if g.board[1][2]==("WX" or "BX"):
                n+=1
            if g.board[2][1]==("WX" or "BX"):
                n+=1
            if g.board[2][2]==("WX" or "BX"):
                n+=1
            if n==1:
                # postoji 1 obrazac razdvojene ploce s jednim ponistenim sredisnjim poljem; ima 4 rotacije
                l=[0, 1, 1, 1, 1, 0]
                for i in range(4):
                    if g.board[l[0]][l[1]]==("WX" or "BX") and g.board[l[2]][l[3]]==("WX" or "BX") and g.board[l[4]][l[5]]==("WX" or "BX"):
                        # razdvojena ploca - treba upisati kod koji ce se izvrsiti
                    rotate(l)
            if n==2:
                # postoje 3 obrasca razdvojene ploce s dva ponistena sredisnja polja; svaki ima 4 rotacije
                for i in range(3):
                    if i==0:
                        l=[0, 1, 1, 1, 2, 1, 3, 1]
                    elif i==1:
                        l=[0, 1, 1, 1, 2, 1, 2, 0]
                    elif i==2:
                        l=[1, 0, 1, 1, 2, 1, 3, 1]
                    for j in range(4):
                        if g.board[l[0]][l[1]]==("WX" or "BX") and g.board[l[2]][l[3]]==("WX" or "BX") and g.board[l[4]][l[5]]==("WX" or "BX") and g.board[l[6]][l[7]]==("WX" or "BX"):
                            # razdvojena ploca - treba upisati kod koji ce se izvrsiti
                        rotate(l)
            if n==3:
                # postoje 4 obrasca razdvojene ploce s tri ponistena sredisnja polja; svaki ima 4 rotacije
                for i in range(4):
                    if i==0:
                        l=[0, 2, 1, 2, 1, 1, 2, 1, 3, 1]
                    elif i==1:
                        l=[0, 2, 1, 2, 1, 1, 2, 1, 2, 0]
                    elif i==2:
                        l=[1, 3, 1, 2, 1, 1, 2, 1, 2, 0]
                    elif i==3:
                        l=[1, 3, 1, 2, 1, 1, 2, 1, 3, 1]
                    for j in range(4):
                        if g.board[l[0]][l[1]]==("WX" or "BX") and g.board[l[2]][l[3]]==("WX" or "BX") and g.board[l[4]][l[5]]==("WX" or "BX") and g.board[l[6]][l[7]]==("WX" or "BX") and g.board[l[8]][l[9]]==("WX" or "BX"):
                            # razdvojena ploca - treba upisati kod koji ce se izvrsiti
                        rotate(l)
        
        if g.game_state!="OVER":
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
