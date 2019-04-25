from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.http import HttpResponseRedirect
from .forms import userForm, shopCreationForm, purchaseForm
from .models import CustomUser, proShop, player
from tournament.models import *
from accounts.models import account, transaction, credits
from django.forms import inlineformset_factory
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
    ShopInlineFormSet = inlineformset_factory(CustomUser, proShop, fields = ('shop_name','head_pro','assistant_pro','shop_adress','pga_number'),can_delete=False)
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
    purchForm = purchaseForm()
    if request.method == "POST":
        postAction = request.POST['action']
        if 'update' in postAction:
            tournamentID = re.match(r"update\s(\d+)", postAction)
            return redirect('updateTournament', id=tournamentID.group(1))
        elif 'remove' in postAction:
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
                "purchase_form":purchForm,
            })
        elif 'purchase':
            form = purchaseForm(request.POST)
            if form.is_valid():
                amount = form.cleaned_data['amount']
                account.addShopFunds(userInfo[0],amount)
            purchForm = purchaseForm
            return render(request, "proShop/shopActions.html", {
                "shopAccount":shopAccount,
                "activeTournaments":activeTournaments,
                "expiredTournaments":expiredTournaments,
                "userInfo":userInfo,
                "creditsSpent":creditsSpent,
                "creditsRecieved":creditsRecieved,
                "purchase_form":purchForm,
            })
    else:
        return render(request, "proShop/shopActions.html", {
            "shopAccount":shopAccount,
            "creditsRecieved":creditsRecieved,
            "creditsSpent":creditsSpent,
            "activeTournaments":activeTournaments,
            "expiredTournaments":expiredTournaments,
            "userInfo":userInfo,
            "purchase_form":purchForm,
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