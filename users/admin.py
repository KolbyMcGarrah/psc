from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import userForm, CustomUserChangeForm
from .models import CustomUser, player, proShop, execUser

UserAdmin.fieldsets += ('Custom fields set', {'fields': ('phoneNumber','userType')}),
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = userForm
    form = CustomUserChangeForm

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(player)
admin.site.register(proShop)
admin.site.register(execUser)