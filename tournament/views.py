from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.http import HttpResponseRedirect, HttpResponse
from django.forms import inlineformset_factory
from .models import tournament, playerResults
from .forms import tournamentForm, existingPlayer
from users.models import player, CustomUser, proShop
from users.forms import playerCreationForm, userForm
import re 
 
# Create your views here.
def registerTournament(request):
    if request.user.is_authenticated and request.user.userType == 3:
        curTournament = tournament()
        curTournament.shop = request.user.userShop
        if request.method == 'POST':
            form = tournamentForm(request.POST)
            if form.is_valid():
                curTournament.tournament_name = form.cleaned_data['tournament_name']
                curTournament.tournament_date = form.cleaned_data['tournament_date']
                curTournament.save() 
                id = curTournament.tournament_id
                return redirect('updateTournament', id=id)
        else: 
            newTourny = tournamentForm()
            return render(request, "tournaments/registerTournament.html", {
            'newTourny':newTourny,
        })
    else: 
        response = HttpResponse(status=403, reason='Invalid User Type')
        return response

def updateTournament(request, id):
    curTournament = tournament.objects.filter(tournament_id = id) #grab the current tournament 
    userAuth = request.user.is_authenticated #set True if user is authenticated
    curShop = request.user.userShop #get Shop name
    userType = request.user.userType #get user type
    playerInlineFormSet = inlineformset_factory(CustomUser, player, fields = ('address','homeCourse'),can_delete=False) #add player form
     #User is authenticated, they are a shop user and they are the shop related to the current tournament 
    tournamentPlayers = playerResults.objects.filter(tournament = curTournament[0])
    if userType == 3 and curShop == curTournament[0].shop and userAuth:        
        if request.method == "POST":
            print('Posting')
            postAction = request.POST['action']
            print(postAction)
            if postAction == 'addPlayer': 
                print('adding player')
                user = CustomUser()
                user_form = userForm(instance=user) # setup a form for the parent
                formset = playerInlineFormSet(instance=user)
                print(user_form)
                return render(request, 'tournaments/updateTournament.html',{
                    'tournamentPlayers': tournamentPlayers,
                    'curTournament' : curTournament,
                    "user_form": user_form,
                    "formset": formset,
                })
            elif postAction == 'savePlayer': 
                print('saving player')
                user_form = userForm(request.POST)
                formset = playerInlineFormSet(request.POST, request.FILES)
                if user_form.is_valid():
                    created_user = user_form.save(commit=False)
                    formset = playerInlineFormSet(request.POST, request.FILES, instance=created_user)
                    if formset.is_valid():
                        created_user.userType=2
                        created_user.save()
                        print(created_user)
                        formset.save()
                        tournyPlayer = playerResults() 
                        tournyPlayer.tournament = curTournament[0]
                        tournyPlayer.player = created_user.userPlayer
                        tournyPlayer.save()
                        print(tournyPlayer)
                        user_form = False
                        formset = False
                        return render(request, 'tournaments/updateTournament.html',{
                            'curTournament' : curTournament,
                            "user_form": user_form,
                            "formset": formset,
                            'tournamentPlayers': tournamentPlayers,
                        })
                    else: 
                        response = HttpResponse(status=500 , reason='This didnt work')
                        return response

            elif 'remove' in postAction:
                buttonID = re.match(r"remove\s(\d+)", postAction)
                print(buttonID.group(1))
                deletePlayer = CustomUser.objects.filter(id=buttonID.group(1))
                playerResults.objects.filter(player=deletePlayer[0].userPlayer, tournament=curTournament[0]).delete()
                return render(request, 'tournaments/updateTournament.html',{
                    'curTournament' : curTournament,
                    'tournamentPlayers': tournamentPlayers,
                }) 
            elif postAction == 'addExisting':
                print('Adding Existing Player')
                existingForm = existingPlayer()
                return render(request, 'tournaments/updateTournament.html',{
                    'curTournament' : curTournament,
                    'existingForm' : existingForm,
                    'tournamentPlayers': tournamentPlayers,
                })
            elif postAction == 'findPlayer':
                print('Finding Player')
                playerSearch = existingPlayer(request.POST)
                if playerSearch.is_valid():
                    fName = request.POST['First_Name']
                    print(fName)
                    lName = request.POST['Last_Name']
                    results = CustomUser.objects.filter(first_name = fName, last_name = lName, userType=2)
                    if not results: 
                        results="None"
                    print('Players Found' + str(results))
                    return render(request, 'tournaments/updateTournament.html',{
                        'curTournament' : curTournament,
                        'results' : results,
                        'tournamentPlayers': tournamentPlayers,
                    })
            elif 'addTo' in postAction:
                playerID = re.match(r"addTo\s(\d+)", postAction)
                print(playerID.group(1))
                newPlayer = player.objects.filter(user = playerID.group(1))
                print('adding player: ', newPlayer)
                checkUnique = playerResults.objects.filter(tournament=curTournament[0], player=newPlayer[0])
                if not checkUnique:
                    addedPlayer = playerResults()
                    addedPlayer.tournament = curTournament[0]
                    addedPlayer.player = newPlayer[0]
                    addedPlayer.save()
                else:
                    print('This player has already been added')
                results=False
                return render(request, 'tournaments/updateTournament.html',{
                            'results':results,
                            'curTournament' : curTournament,
                            'tournamentPlayers': tournamentPlayers,
                        })
            else:
                response = HttpResponse(status=500 , reason='This didnt work')
                return response  
                
        else:
            print(str(request.method))
            return render(request, 'tournaments/updateTournament.html',{
                'curTournament' : curTournament,
                'tournamentPlayers': tournamentPlayers,
            })
    else: 
        response = HttpResponse(status=403, reason='You are not Authorized to view this page')
        return response 

def tournamentResults(request, id):
    curTournament = tournament.getTournamentFromID(id)
    tournamentPlayers = playerResults.getTournamentPlayers(curTournament)
    return render(request, 'tournaments/tournamentResults.html',{
        "curTournament" : curTournament,
        "tournamentPlayers" : tournamentPlayers,
    })
