from django.urls import path
from . import views

urlpatterns = [
    path('registerTournament/', views.registerTournament, name='registerTournament'),
    path('updateTournament/<id>', views.updateTournament, name='updateTournament'),
    path('tournamentResults/<id>', views.tournamentResults, name='tournamentResults'),
    path('finalizeResults/<id>', views.finalizeResults, name='finalizeResults'),
    path('confirmResults/<id>', views.tournamentResults, name='confirmResults'),
    path('fundsOver/<id>', views.fundsOver, name='fundsOver'),
    path ('fundsUnder/<id>', views.fundsUnder, name='fundsUnder'),
    path('Success', views.Success, name='Success'),
    path('insufficientCredits/<id>',views.insufficientCredits, name='insufficientCredits')
]