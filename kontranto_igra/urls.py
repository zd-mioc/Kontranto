from django.contrib import admin
from django.urls import path
from kontranto_igra import views


urlpatterns = [
    path("", views.index, name="index"),
    path("pravila", views.pravila, name="pravila"),
    path("show_board", views.show_board, name="show_board"),
    path("new_game", views.new_game, name="new_game"),
    path("join_game", views.join_game, name="join_game"),
    path("move", views.move, name="move"),
    path("game_state", views.game_state, name="game_state"),
    path("prijelaz", views.prijelaz, name="prijelaz"),
    path("get_move", views.get_move, name="get_move")
    # path("update_info", views.update_info, name="update_info")
]
