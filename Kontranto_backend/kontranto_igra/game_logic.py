from random import *
from time import localtime

def random_game_id():
    # ...
    #generira game_id
    # ...
    return "<neki_random_generirani_game_id_s_backenda>"

def BlackOrWhite(color): #univerzalna funkcija - može i kod jednog i kod drugog igraca
    l=['black','white']
    if color=='':
        return choice(l)
    elif color=='white':
        return 'black'
    else:
        return 'white'

def status(game_id):
    # ...
    #provjerava je li game_id valjan
    # ...
    return "Ako je game_id valjan vraća 'OK', u suprotnom vraća 'Greška. Nevažeća igra'."

def last_move_timestamp(): #bilježi vrijeme kada je potez odigran
    t=localtime()
    l=[]
    for i in range (6):
        if t[i]<10:
            l.append('0'+str(t[i]))
        else:
            l.append(t[i])
    time="{}.{}.{}., {}:{}:{}".format(l[2],l[1],l[0],l[3],l[4],l[5])
    return time