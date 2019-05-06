from django import forms 
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, player, proShop

class userForm(UserCreationForm): 
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name','phoneNumber')

class CustomUserChangeForm(UserChangeForm): 
    class Meta:  
        model = CustomUser
        fields = UserChangeForm.Meta.fields

class shopCreationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(shopCreationForm, self).__init__(*args, **kwargs)
        self.fields['pga_number'].label = "PGA Number"
    class Meta:
        model = proShop
        fields = ('shop_name','head_pro','assistant_pro','shop_adress','pga_number', 'section')
        
class playerCreationForm(forms.ModelForm):
    class Meta: 
        model = player
        fields = ('address','homeCourse')

class purchaseForm(forms.Form):
    amount = forms.DecimalField(max_digits=11,decimal_places=2)
