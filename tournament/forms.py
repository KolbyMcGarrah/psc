from django import forms 
from django.forms.models import inlineformset_factory, modelformset_factory
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from users.models import CustomUser, player, proShop
from .models import tournament, playerResults
from django.forms import widgets, DateInput

class tournamentForm(forms.ModelForm):
    tournament_date = forms.DateField(widget=forms.DateInput(format=['%Y-%m-%d', '%m-%d-%Y', '%m/%d/%Y', '%Y/%m/%d']))
    class Meta:
        model = tournament
        fields = ('tournament_name','tournament_date', 'prize_pool')
    
class existingPlayer(forms.Form):
    First_Name = forms.CharField()
    Last_Name = forms.CharField()

class playerResultForm(forms.ModelForm):
    class Meta: 
        model = playerResults
        exclude = ('player','tournament')

playerResultFormSet = modelformset_factory(playerResults, form=playerResultForm, extra=0)