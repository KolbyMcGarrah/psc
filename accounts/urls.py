from django.urls import path
from . import views

urlpatterns = [
    path('payment/', views.payment, name = 'payment'),
    path('success/', views.successfulTransaction, name = 'successfulTransaction'),
    path('error/', views.failedTransaction, name = 'failedTransaction'),
]