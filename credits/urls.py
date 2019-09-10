from django.urls import path
from . import views

urlpatterns = [
    path('spendCredits/<id>', views.spendCredits, name='spendCredits'),
    path('authorizeTransaction/', views.authorizeTransaction, name='authorizeTransaction'),
    path('billing/', views.billing, name='billing'),
    path('stripeConfirm', views.stripeConfirm, name='stripeConfirm'),
]
