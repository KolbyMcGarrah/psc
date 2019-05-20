from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.http import HttpResponseRedirect, HttpResponse
from django.forms import inlineformset_factory, formset_factory, modelformset_factory
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import tournament, playerResults
from .forms import tournamentForm, existingPlayer, playerResultFormSet
from accounts.models import account, transaction
from users.models import player, CustomUser, proShop
from users.forms import playerCreationForm, userForm
import re 
 
def shop_test(user):
    return CustomUser.isShop(user)

@login_required
@user_passes_test(shop_test,login_url='/', redirect_field_name=None)
def registerTournament(request):
    curTournament = tournament()
    curTournament.shop = request.user.userShop
    if request.method == 'POST':
        form = tournamentForm(request.POST)
        if form.is_valid():
            curTournament.tournament_name = form.cleaned_data['tournament_name']
            curTournament.tournament_date = form.cleaned_data['tournament_date']
            curTournament.prize_pool = form.cleaned_data['prize_pool']
            curTournament.save() 
            id = curTournament.tournament_id
            return redirect('updateTournament', id=id)
        else:
            print(form.errors)
    else: 
        newTourny = tournamentForm()
        return render(request, "tournaments/registerTournament.html", {
        'newTourny':newTourny,
    })

@login_required
@user_passes_test(shop_test,login_url='/', redirect_field_name=None)
def updateTournament(request, id):    
    curTournament = tournament.getTournamentFromID(id) #grab the current tournament 
    curShop = request.user.userShop #get Shop name
    userType = request.user.userType #get user type
    playerInlineFormSet = inlineformset_factory(CustomUser, player, fields = ('address','homeCourse'),can_delete=False) #add player form
    tournamentPlayers = playerResults.objects.filter(tournament = curTournament)
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
                    formset.save()
                    playerAccount = account.createPlayerAccount(created_user)
                    playerAccount.save()
                    tournyPlayer = playerResults() 
                    tournyPlayer.tournament = curTournament
                    tournyPlayer.player = created_user.userPlayer
                    tournyPlayer.save()
                    user_form = False
                    formset = False
                    return render(request, 'tournaments/updateTournament.html',{
                        'curTournament' : curTournament,
                        "user_form": user_form,
                        "formset": formset,
                        'tournamentPlayers': tournamentPlayers,
                    })
                else:
                    print(formset.errors)
                    response = HttpResponse(status=500 , reason='This didnt work')
                    print 
                    return response

        elif 'remove' in postAction:
            buttonID = re.match(r"remove\s(\d+)", postAction)
            print(buttonID.group(1))
            deletePlayer = CustomUser.objects.filter(id=buttonID.group(1))
            playerResults.objects.filter(player=deletePlayer[0].userPlayer, tournament=curTournament).delete()
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
            checkUnique = playerResults.objects.filter(tournament=curTournament, player=newPlayer[0])
            if not checkUnique:
                addedPlayer = playerResults()
                addedPlayer.tournament = curTournament
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
        if 'finalize' in postAction:
            tournamentID = re.match(r"finalize\s(\d+)", postAction)
            curTournament.status = 3
            curTournament.save()
            return redirect('tournamentResults', id=tournamentID.group(1))
        else:
            response = HttpResponse(status=500 , reason='This didnt work')
            return response  
    if curTournament.status == 3:
            return redirect('tournamentResults', id=curTournament.tournament_id)   
    else:
        print(str(request.method))
        return render(request, 'tournaments/updateTournament.html',{
            'curTournament' : curTournament,
            'tournamentPlayers': tournamentPlayers,
        })

@login_required
@user_passes_test(shop_test,login_url='/', redirect_field_name=None)
def tournamentResults(request, id):
    curTournament = tournament.getTournamentFromID(id)
    tournamentPlayers = playerResults.getTournamentPlayers(curTournament)
    if request.method == "POST":
        formSet=playerResultFormSet(request.POST,request.FILES)
        totalAmount = 0.00
        for form in formSet:
            if form.is_valid():
                curAmount = float(form.cleaned_data['amount_won'])
                totalAmount += curAmount
                form.save()
        print(totalAmount)
        getNextPage = tournament.balanceWinnings(curTournament,totalAmount)
        if getNextPage == "Exact":
            return redirect('finalizeResults', id=curTournament.tournament_id)
        elif getNextPage == "Over":
            return redirect('fundsOver', id=curTournament.tournament_id)
        else: 
            return redirect('fundsUnder', id=curTournament.tournament_id)
    else:
        formSet = playerResultFormSet(queryset=tournamentPlayers)
        return render(request, 'tournaments/tournamentResults.html',{
            "curTournament" : curTournament,
            "tournamentPlayers" : tournamentPlayers,
            "forms":formSet,
        })

@login_required
@user_passes_test(shop_test,login_url='/', redirect_field_name=None)
def finalizeResults(request, id):
    curTournament = tournament.getTournamentFromID(id)
    tournamentPlayers = playerResults.objects.filter(tournament=curTournament)
    tournamentWinners = []
    for field in tournamentPlayers:
        if field.amount_won > 0: 
            tournamentWinners.append(field)
    if request.method == "POST": 
        action = request.POST['action']
        if action == 'confirm':
            if tournament.finalizeTournament(tournamentWinners,curTournament) == 'Success':
                return redirect('Success')
            else:
                return redirect('insufficientCredits',curTournament.tournament_id)
        else:
            return redirect('tournamentResults',id)
    else:
        return render(request, 'tournaments/finalizeResults.html', {
            "curTournament": curTournament, 
            "tournamentPlayers": tournamentWinners,
        })

@login_required
@user_passes_test(shop_test,login_url='/', redirect_field_name=None)
def fundsUnder(request,id):
    curTournament= tournament.getTournamentFromID(id)
    tournamentPlayers = playerResults.objects.filter(tournament=curTournament)
    totalAmount = 0.00
    for play in tournamentPlayers:
        totalAmount += float(play.amount_won)
    difference = float(curTournament.prize_pool) - totalAmount
    if request.method == "POST":
        if 'confirm' in request.POST['action']:            
            buttonID = re.match(r"confirm\s(\d+)", request.POST['action'])
            curTournament.prize_pool = totalAmount
            curTournament.save()
            return redirect('finalizeResults',buttonID.group(1))
        else:
            buttonID = re.match(r"adjust\s(\d+)", request.POST['action'])
            return redirect('updateTournament',buttonID.group(1))
    else:
        return render(request, 'tournaments/fundsUnder.html',{
            'curTournament':curTournament,
            'difference':difference,
        })

@login_required
@user_passes_test(shop_test,login_url='/', redirect_field_name=None)
def fundsOver(request,id):
    curTournament= tournament.getTournamentFromID(id)
    tournamentPlayers = playerResults.objects.filter(tournament=curTournament)
    totalAmount = 0.00
    for play in tournamentPlayers:
        totalAmount += float(play.amount_won)
    difference = totalAmount - float(curTournament.prize_pool)
    if request.method == "POST":
        if request.POST['action'] == 'confirm':
            curTournament.prize_pool = totalAmount
            curTournament.save()
            return redirect('finalizeResults',id)
        else:
            buttonID = re.match(r"adjust\s(\d+)", request.POST['action'])
            return redirect('updateTournament',buttonID.group(1))
    else:
        return render(request, 'tournaments/fundsOver.html',{
            'curTournament':curTournament,
            'difference':difference,
        })

@login_required
@user_passes_test(shop_test,login_url='/', redirect_field_name=None)
def Success(request):
    return render(request, "tournaments/Success.html")

@login_required
@user_passes_test(shop_test,login_url='/', redirect_field_name=None)
def insufficientCredits(request,id):
    curTournament=tournament.getTournamentFromID(id)
    userAccount = account.getAccount(request.user)
    difference = curTournament.prize_pool - userAccount.current_balance
    return render(request, "tournaments/insufficientCredits.html",{
        "difference":difference,
    })

@login_required
@user_passes_test(shop_test,login_url='/', redirect_field_name=None)
def tournamentHistory(request, id): 
    curTournament = tournament.getTournamentFromID(id)
    results = playerResults.getTournamentPlayers(curTournament)
    return render(request, "tournaments/tournamentHistory.html",{
        "results":results,
        "tournament":curTournament,
    })


