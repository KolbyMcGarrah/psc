from django.urls import path
from . import views

urlpatterns = [
    path('playerSignup/', views.playerRegistration, name='registerPlayer'),   
    path('registerShop/', views.registerShop, name = 'registerShop'),
    path('shopActions/', views.shopActions, name = 'shopActions'),
    path('purchaseFunds/', views.purchaseFunds, name = 'purchaseFunds'),
    path('playerActions/', views.playerActions, name = 'playerActions'), 
]