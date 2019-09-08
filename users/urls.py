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
]
