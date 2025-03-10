from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from django.views import generic
from django.http import HttpResponseRedirect
from django.contrib import messages
from .forms import *
from .models import CustomUser, proShop, player, execUser
from tournament.models import *
from tournament.forms import existingPlayer
from accounts.models import account, transaction, credits, BillingEvent
from django.forms import inlineformset_factory, BaseInlineFormSet
from pga_events.models import PGA_Event as pg, results as res
from pga_events.forms import searchPlayer
import re

def shop_test(user):
    return CustomUser.isShop(user)

def player_test(user):
    return CustomUser.isPlayer(user)

def exec_test(user):
    return CustomUser.isExec(user)

def playerRegistration(request):
    user = CustomUser()
    user_form = userForm(instance=user)
    playerInlineFormSet = inlineformset_factory(CustomUser, player, form=playerCreationForm,can_delete=False)
    formset = playerInlineFormSet(instance=user)
    if request.method == "POST":
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
                request.session['userID'] = created_user.id
                return redirect("createPin")
    return render(request, "signup.html",{
        "user_form":user_form,
        "formset": formset,
    })

def registerShop(request):
    success_url = reverse_lazy('login')
    user = CustomUser()
    user_form = userForm(instance=user) # setup a form for the parent
    ShopInlineFormSet = inlineformset_factory(CustomUser, proShop, form=shopCreationForm,can_delete=False)
    formset = ShopInlineFormSet(instance=user)
    if request.method == "POST":
        user_form = userForm(request.POST)
        formset = ShopInlineFormSet(request.POST, request.FILES)
        if user_form.is_valid():
            created_user = user_form.save(commit=False)
            formset = ShopInlineFormSet(request.POST, request.FILES, instance=created_user)
            if formset.is_valid():
                created_user.userType =3
                created_user.save()
                formset.save()
                shopAccount = account.createShopAccount(created_user)
                shopAccount.save()
                return HttpResponseRedirect(success_url)
    return render(request, "registerShop.html", {
        "user_form": user_form,
        "formset": formset,
    })

@login_required
@user_passes_test(shop_test,login_url='/', redirect_field_name=None)
def shopActions(request):
    activeTournaments = tournament.getActiveTournaments(request.user.userShop)
    expiredTournaments = tournament.objects.filter(shop=request.user.userShop, status=4)
    userInfo = CustomUser.objects.filter(id = request.user.id)
    shopAccount = account.getAccount(request.user)
    creditsRecieved = transaction.getRecievedTransactions(shopAccount)
    creditsSpent = transaction.getPayedTransactions(shopAccount)
    approvedEvents = BillingEvent.getApprovedEvents(request.user)
    searchForm = searchPlayer()
    if request.method == "POST":
        postAction = request.POST['action']
        print(postAction)
        if 'update' in postAction:
            print('updating')
            tournamentID = re.match(r"update\s(\d+)", postAction)
            return redirect('updateTournament', id=tournamentID.group(1))
        elif 'remove' in postAction:
            print('removing')
            tournamentID = re.match(r"remove\s(\d+)", postAction)
            curTournament = tournament.objects.get(tournament_id = tournamentID.group(1))
            curTournament.status = 2 #set the tournament status to abandoned
            curTournament.save()
            return render(request, "proshop/shopActions.html", {
                "shopAccount":shopAccount,
                "activeTournaments":activeTournaments,
                "expiredTournaments":expiredTournaments,
                "userInfo":userInfo,
                "creditsSpent":creditsSpent,
                "creditsRecieved":creditsRecieved,
                "searchForm":searchForm,
            })
        elif postAction == 'search':
            print('searching for a player')
            form = searchPlayer(request.POST)
            if form.is_valid():
                first = request.POST['First_Name']
                last = request.POST['Last_Name']
                playerResults = player.searchPlayer(first,last)
                return render(request, "proshop/shopActions.html", {
                    "shopAccount":shopAccount,
                    "activeTournaments":activeTournaments,
                    "expiredTournaments":expiredTournaments,
                    "userInfo":userInfo,
                    "creditsSpent":creditsSpent,
                    "creditsRecieved":creditsRecieved,
                    "searchForm":searchForm,
                    "playerResults":playerResults,
                })
        elif 'spend' in postAction:
            print('spending')
            spendID = re.match(r"spend\s(\d+)", postAction)
            return redirect('spendCredits', id=spendID.group(1))

        elif 'approve' in postAction:
            approveID = re.match(r"approve(\d+)",postAction)
            BillingEvent.completeEvent(BillingEvent.getEventByID(approveID.group(1)))
            return render(request, "proshop/shopActions.html", {
                    "shopAccount":shopAccount,
                    "activeTournaments":activeTournaments,
                    "expiredTournaments":expiredTournaments,
                    "userInfo":userInfo,
                    "creditsSpent":creditsSpent,
                    "creditsRecieved":creditsRecieved,
                    "searchForm":searchForm})
        elif postAction == 'allEvents':
            return redirect('billing')
    else:
        return render(request, "proshop/shopActions.html", {
            "shopAccount":shopAccount,
            "creditsRecieved":creditsRecieved,
            "creditsSpent":creditsSpent,
            "activeTournaments":activeTournaments,
            "expiredTournaments":expiredTournaments,
            "userInfo":userInfo,
            "searchForm":searchForm,
            "events":approvedEvents,
        })

@login_required
@user_passes_test(shop_test,login_url='/', redirect_field_name=None)
def purchaseFunds(request):
    curShop = request.user
    form = purchaseForm()
    if request.method == "POST":
        form = purchaseForm(request.POST)
        if form.is_valid():
            request.session['amount'] = float(form.cleaned_data['amount'])
        return redirect("payment")
    else:
        return render(request, "proshop/purchaseFunds.html",{
            "form":form,
        })

@login_required
@user_passes_test(exec_test,login_url='/', redirect_field_name=None)
def execHome(request):
    user = request.user
    curSection = user.execFields.section
    sectionCredits = credits.getSectionCredits(curSection)
    totalSectionCredits = credits.totalSectionCredits(curSection)
    expiringSectionCredits = credits.expiringSecCredits(curSection)
    expiredSectionCredits = credits.expiredSecCredits(curSection)
    activeSecCredits = credits.activeSecCredits(curSection)
    mostActive = tournament.getMostActiveShops(curSection, 3)
    leastActive = tournament.getLeastActiveShops(curSection, 3)
    upcomingEvents = pg.upcomingEvents(user.execFields)
    eventHistory = pg.pastEvents(user.execFields)
    print(eventHistory)
    if request.method == "POST":
        postRequest = request.POST['action']
        if 'update' in postRequest:
            eventID = re.match(r"update(.*)", postRequest)
            request.session['event_id'] = eventID.group(1)
            return redirect("update")
        elif 'remove' in postRequest:
            eventID = re.match(r"remove(.*)", postRequest)
            pg.removeEvent(eventID.group(1))
            upcomingEvents = pg.upcomingEvents(user.execFields)
            return render(request, "exec/execHome.html", {
                "sectionCredits":sectionCredits,
                "totalCredits":totalSectionCredits,
                "expiringCredits":expiringSectionCredits,
                "expiredCredits":expiredSectionCredits,
                "activeCredits":activeSecCredits,
                "mostActive":mostActive,
                "leastActive":leastActive,
                "upcomingEvents":upcomingEvents,
                "eventHistory":eventHistory,
            })
    else:
        return render(request, "exec/execHome.html", {
            "sectionCredits":sectionCredits,
            "totalCredits":totalSectionCredits,
            "expiringCredits":expiringSectionCredits,
            "expiredCredits":expiredSectionCredits,
            "activeCredits":activeSecCredits,
            "mostActive":mostActive,
            "leastActive":leastActive,
            "upcomingEvents":upcomingEvents,
            "eventHistory":eventHistory
        })

def createPin(request):
    if 'userID' in request.session:
        userID = request.session['userID']
        currentUser = CustomUser.objects.filter(id=userID)[0]
    else:
        return HttpResponseRedirect(reverse_lazy('login'))
    if request.method == "POST":
        pinForm = pinCreation(request.POST)
        if pinForm.is_valid():
            player.updatePin(currentUser, pinForm.cleaned_data['Account_Pin'])
            del request.session['userID']
            return redirect('login')
        else:
            return render(request, 'player/createPin.html',{
                'form':pinForm,
            })
    else:
        pinForm = pinCreation()
        return render(request,'player/createPin.html',{
            'form':pinForm,
        })

@login_required
@user_passes_test(player_test)
def playerEdit(request):
    if request.session['playerID']:
        editUser = CustomUser.objects.filter(id=request.session['playerID'])[0]

    else:
        return redirect('home')

@login_required
@user_passes_test(player_test,login_url='/', redirect_field_name=None)
def playerOverview(request):
    curPlayer = request.user.userPlayer
    playerAccount = account.getPlayerAccount(curPlayer)
    totalActive = credits.getTotalActiveCredits(playerAccount)
    expiringCredits = credits.totalExpiringCredits(playerAccount)
    expiredCredits = credits.totalExpiredCredits(playerAccount)
    #lastTournament = tournament.getPlayerTournaments(curPlayer)[0].tournament_name
    highestPrize = playerResults.getHighestPrize(curPlayer)
    return render(request,'player/playerOverview.html',{
        "totalActive":totalActive,
        "expiringCredits":expiringCredits,
        "expiredCredits":expiredCredits,
        #"lastTournament":lastTournament,
        "highestPrize":highestPrize,
    })

@login_required
@user_passes_test(player_test,login_url='/', redirect_field_name=None)
def playerCredits(request):
    curPlayer = request.user.userPlayer
    playerAccount = account.getPlayerAccount(curPlayer)
    activeCredits = credits.getActiveCredits(playerAccount)
    expiringCredits = credits.getExpiringCredits(playerAccount)
    expiredCredits = credits.getExpiredCredits(playerAccount)
    creditsRecieved = transaction.getRecievedTransactions(playerAccount)
    creditsSpent = transaction.getPayedTransactions(playerAccount)
    return render(request, 'player/playerCredits.html',{
        "activeCredits":activeCredits,
        "expiringCredits":expiringCredits,
        "expiredCredits":expiredCredits,
        "creditsRecieved":creditsRecieved,
        "creditsSpent":creditsSpent,
    })
    
@login_required
@user_passes_test(player_test,login_url='/', redirect_field_name=None)
def playerTournaments(request):
    curPlayer = request.user.userPlayer
    tournaments = playerResults.getPlayerResults(curPlayer)
    return render(request,'player/playerTournaments.html',{
        "tournaments":tournaments,
    })

@login_required
@user_passes_test(player_test,login_url='/', redirect_field_name=None)
def trade(request):
    curPlayer = request.user.userPlayer
    playerAccount = account.getPlayerAccount(curPlayer)
    return render(request, "player/trade.html",{
        "playerAccount":playerAccount,
    })

@login_required
@user_passes_test(player_test,login_url='/', redirect_field_name=None)
def playerProfile(request):
    curUser = request.user
    return render(request,"player/playerProfile.html",{
        "curUser":curUser,
    })

def shopOverview(request):
    return render(request, "proshop/shopOverview.html")
