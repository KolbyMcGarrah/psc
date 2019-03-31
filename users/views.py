from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.http import HttpResponseRedirect
from .forms import userForm, shopCreationForm
from .models import CustomUser, proShop, player
from tournament.models import *
from accounts.models import account, transaction
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
    activeTournaments = tournament.objects.filter(shop=request.user.userShop, active=True)
    expiredTournaments = tournament.objects.filter(shop=request.user.userShop, active=False)
    userInfo = CustomUser.objects.filter(id = request.user.id)
    shopAccount = account.getAccount(request.user)
    creditsRecieved = transaction.getRecievedTransactions(shopAccount)
    creditsSpent = transaction.getPayedTransactions(shopAccount)
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
            })
        elif 'purchase':
            return render(request, "proShop/purchaseFunds.html")
    else:
        return render(request, "proShop/shopActions.html", {
            "shopAccount":shopAccount,
            "creditsRecieved":creditsRecieved,
            "creditsSpent":creditsSpent,
            "activeTournaments":activeTournaments,
            "expiredTournaments":expiredTournaments,
            "userInfo":userInfo,
        })
def playerActions(request):
    upcomingTournaments = tournament.objects.filter(players=request.user.userPlayer, active=True)
    previousTournaments = tournament.objects.filter(players=request.user.userPlayer, active=True)
    playerAccount = account.getAccount(request.user)
    userInfo = CustomUser.objects.filter(id = request.user.id)
    return render(request, "player/playerActions.html",{
        "upcomingTournaments":upcomingTournaments, 
        "previousTournaments":previousTournaments,
        "userInfo":userInfo,
        "playerAccount":playerAccount,
    })

def purchaseFunds(request):
    curShop = request.user
    if request.method == "POST":
        account.addShopFunds(curShop, 300)
        return render(request, "proShop/purchaseFunds.html")
    else: 
        return render(request, "proShop/purchaseFunds.html")