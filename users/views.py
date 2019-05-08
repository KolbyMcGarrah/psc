from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.http import HttpResponseRedirect
from .forms import userForm, shopCreationForm, spendForm
from .models import CustomUser, proShop, player, execUser
from tournament.models import *
from tournament.forms import existingPlayer
from accounts.models import account, transaction, credits
from django.forms import inlineformset_factory, BaseInlineFormSet
import re


def playerRegistration(request):
    success_url = reverse_lazy('login')
    user = CustomUser()
    user_form = userForm(instance=user)

    playerInlineFormSet = inlineformset_factory(CustomUser, player, fields = ('address','homeCourse'),can_delete=False)
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
                return HttpResponseRedirect(success_url)
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

def shopActions(request):
    activeTournaments = tournament.getActiveTournaments(request.user.userShop)
    expiredTournaments = tournament.objects.filter(shop=request.user.userShop, status=4)
    userInfo = CustomUser.objects.filter(id = request.user.id)
    shopAccount = account.getAccount(request.user)
    creditsRecieved = transaction.getRecievedTransactions(shopAccount)
    creditsSpent = transaction.getPayedTransactions(shopAccount)
    searchForm = existingPlayer()
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
            curTournament.active = False
            curTournament.save()
            return render(request, "proShop/shopActions.html", {
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
            form = existingPlayer(request.POST)
            if form.is_valid():
                playerResults = CustomUser.objects.filter(first_name = form.cleaned_data['First_Name'], last_name = form.cleaned_data['Last_Name'])
                return render(request, "proShop/shopActions.html", {
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
    else:
        return render(request, "proShop/shopActions.html", {
            "shopAccount":shopAccount,
            "creditsRecieved":creditsRecieved,
            "creditsSpent":creditsSpent,
            "activeTournaments":activeTournaments,
            "expiredTournaments":expiredTournaments,
            "userInfo":userInfo,
            "searchForm":searchForm,
        })
def playerActions(request):
    upcomingTournaments = tournament.objects.filter(players=request.user.userPlayer, status=True)
    previousTournaments = playerResults.getPlayerResults(request.user.userPlayer)
    playerAccount = account.getAccount(request.user)
    playerCredits = credits.myCredits(request.user)
    creditsRecieved = transaction.getRecievedTransactions(playerAccount)
    creditsSpent = transaction.getPayedTransactions(playerAccount)
    userInfo = CustomUser.objects.filter(id = request.user.id)
    return render(request, "player/playerActions.html",{
        "upcomingTournaments":upcomingTournaments, 
        "previousTournaments":previousTournaments,
        "creditsRecieved":creditsRecieved,
        "creditsSpent":creditsSpent,
        "userInfo":userInfo,
        "playerAccount":playerAccount,
        "playerCredits":playerCredits,
    })

def purchaseFunds(request):
    curShop = request.user
    form = purchaseForm()
    if request.method == "POST":
        form = purchaseForm(request.POST)
        if form.is_valid():
            request.session['amount'] = float(form.cleaned_data['amount'])
        return redirect("payment")
    else: 
        return render(request, "proShop/purchaseFunds.html",{
            "form":form,
        })

def execHome(request): 
    user = request.user
    curSection = user.execFields.section
    sectionCredits = credits.getSectionCredits(curSection)
    return render(request, "exec/execHome.html", {
        "sectionCredits":sectionCredits,
    })

def spendCredits(request,id):
    curShop = request.user.userShop
    curPlayer = CustomUser.objects.filter(id=id)[0]
    playerAccount = account.getAccount(curPlayer)
    playerCredits = credits.myCredits(curPlayer)
    shopAccount = account.getShopAccount(curShop)
    form = spendForm()
    if request.method == "POST":
        form = spendForm(request.POST)
        if form.is_valid():
            result = credits.spendCredits(playerAccount,shopAccount,form.cleaned_data['Amount'], form.cleaned_data['Item_Description'])
            if result == True:
                return redirect('home')
            else:
                print('')
                return redirect('spendCredits',id=id)
    else:    
        return render(request, "proShop/spendCredits.html",{
            "playerCredits":playerCredits,
            "shop":curShop,
            "player":curPlayer,
            "playerAccount":playerAccount,
            "form":form,
        })
    
    