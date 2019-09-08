from django import forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, player, proShop

class userForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name','phoneNumber')

class tourneyUserForm(UserCreationForm):
    """
    A UserCreationForm with optional password inputs.
    """
    def __init__(self,*args,**kwargs):
        super(tourneyUserForm, self).__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        self.fields['password1'].widget = forms.HiddenInput()
        self.fields['password2'].widget = forms.HiddenInput()
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username','email','first_name','last_name','phoneNumber')


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

class pinCreation(forms.Form):
    Account_Pin = forms.CharField(min_length=4,max_length=4, widget=forms.PasswordInput)
    Confirm_Pin = forms.CharField(min_length=4,max_length=4, widget=forms.PasswordInput)
    def __init__(self, *args, **kwargs):
        super(pinCreation,self).__init__(*args, **kwargs)
        self.fields['Account_Pin'].widget.attrs['type'] = "number"
        self.fields['Account_Pin'].widget.attrs['placeholder'] = '0000'
        self.fields['Confirm_Pin'].widget.attrs['type'] = "number"
        self.fields['Confirm_Pin'].widget.attrs['placeholder'] = '0000'
    def clean(self):
        cleaned_data = super().clean()
        Account_Pin = cleaned_data.get("Account_Pin")
        Confirm_Pin = cleaned_data.get("Confirm_Pin")
        if Account_Pin and Confirm_Pin:
            if Account_Pin != Confirm_Pin:
                raise forms.ValidationError(
                    "The Confirm Pin did not match the Account Pin. Please try again."
                )
            elif Account_Pin.isnumeric() == False:
                raise forms.ValidationError("The PIN must be numeric.")

class userEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name','phoneNumber')

class playerEditForm(forms.ModelForm):
    class Meta:
        model = player
        fields = ('homeCourse', 'address')
