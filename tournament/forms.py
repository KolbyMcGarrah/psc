from django import forms 
from django.forms.models import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from users.models import CustomUser, player, proShop
from .models import tournament, playerResults

class tournamentForm(forms.ModelForm):
    class Meta:
        model = tournament
        fields = ('tournament_name','tournament_date')
class existingPlayer(forms.Form):
    First_Name = forms.CharField()
    Last_Name = forms.CharField()

class playerResultForm(forms.ModelForm):
    class Meta: 
        model = playerResults
        fields = ('player','amount_won', 'position')

