from django.contrib import admin
from .models import PGA_Event, results

# Register your models here.
admin.site.register(PGA_Event)
admin.site.register(results)