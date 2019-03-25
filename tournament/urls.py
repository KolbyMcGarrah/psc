from django.urls import path
from . import views

urlpatterns = [
    path('registerTournament/', views.registerTournament, name='registerTournament'),
    path('updateTournament/<id>', views.updateTournament, name='updateTournament'),
]