from django.contrib import admin
from .models import account, transaction, credits, BillingEvent
# Register your models here.

admin.site.register(account)
admin.site.register(transaction)
admin.site.register(credits)
admin.site.register(BillingEvent)