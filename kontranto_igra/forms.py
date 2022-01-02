from django import forms

class NewGameForm(forms.Form):
  player_id = forms.CharField(label='Username', max_length=100)

class JoinGameForm(forms.Form):
  player_id = forms.CharField(label='Username', max_length=100)
  game_id = forms.CharField(label='Game ID', max_length=100)
