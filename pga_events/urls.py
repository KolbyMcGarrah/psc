from django.urls import path
from . import views

urlpatterns = [
    path('schedule/', views.schedule, name = 'schedule'),
    path('setResults/', views.setResults, name = 'setResults'),
    path('confirmPrize/', views.confirmPrize, name = 'confirmPrize'),
    path('update/', views.update, name = 'update')
]