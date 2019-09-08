from django import forms

class spendForm(forms.Form):
    Amount = forms.DecimalField(max_digits=11, decimal_places=2)
    Item_Description = forms.CharField()

class playerAuthPurchaseForm(forms.Form):
    Player_Pin = forms.CharField(min_length=4,max_length=4, widget=forms.PasswordInput)
    def __init__(self, *args, **kwargs):
        super(playerAuthPurchaseForm,self).__init__(*args, **kwargs)
        self.fields['Player_Pin'].widget.attrs['type'] = "number"
        self.fields['Player_Pin'].widget.attrs['placeholder'] = '4 digit pin'

class purchaseForm(forms.Form):
    amount = forms.DecimalField(max_digits=11,decimal_places=2)
