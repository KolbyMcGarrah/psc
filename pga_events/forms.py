from django.forms import widgets, DateInput
from django import forms
from .models import PGA_Event, results
from django.forms.models import inlineformset_factory, modelformset_factory

class eventScheduleForm(forms.ModelForm):
    event_date = forms.DateField(widget=forms.SelectDateWidget())
    class Meta:
        model = PGA_Event
        fields = ('event_name','event_date','number_of_players', 'prize_pool','host_shop')

class searchPlayer(forms.Form):
    First_Name = forms.CharField(max_length=40, required = False)
    Last_Name = forms.CharField(max_length=40, required = False)

class resultsForm(forms.ModelForm):
    class Meta:
        model = results
        exclude=('PGA_Event','player','added_on')

resultFormSet = modelformset_factory(results, form=resultsForm, extra=0)

    