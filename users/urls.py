from django.urls import path
from . import views

urlpatterns = [
    path('playerSignup/', views.playerRegistration, name='registerPlayer'),
    path('registerShop/', views.registerShop, name = 'registerShop'),
    path('shopActions/', views.shopActions, name = 'shopActions'),
    path('playerActions/', views.playerActions, name = 'playerActions'),
    path('purchaseFunds/', views.purchaseFunds, name = 'purchaseFunds'),
    path('execHome/', views.execHome, name = 'execHome'),
    path('createPin/', views.createPin, name='createPin'),
    path('playerOverview/', views.playerOverview, name='playerOverview'),
    path('playerCredits/', views.playerCredits, name='playerCredits'),
    path('playerTournaments/', views.playerTournaments, name='playerTournaments'),
    path('trade/', views.trade, name='trade'),
    path('playerProfile/', views.playerProfile, name='playerProfile'),
]
