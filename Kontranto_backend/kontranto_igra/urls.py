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
    path("board_state", views.board_state, name="board_state")
]
