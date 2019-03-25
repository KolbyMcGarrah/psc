from django.contrib import admin
from .models import account, transaction
# Register your models here.

admin.site.register(account)
admin.site.register(transaction)