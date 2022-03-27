from django.contrib import admin
from django.urls import path
from kontranto_igra import views

urlpatterns = [
    path("", views.index, name="index"),
    path("rules", views.game_rules, name="game_rules"),
    path("new_game", views.new_game, name="new_game"),
    path("join_game", views.join_game, name="join_game"),
    path("show_board/<game_id>/<player_id>",
         views.show_board,
         name="show_board"),
    path("game_state/<game_id>/<player_id>",
         views.game_state,
         name="game_state"),
    path("move", views.move, name="move"),
]
