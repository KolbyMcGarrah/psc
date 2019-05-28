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
@login_required
@user_passes_test(player_test,login_url='/', redirect_field_name=None)
def playerActions(request):
    upcomingTournaments = tournament.objects.filter(players=request.user.userPlayer, status=True)
    previousTournaments = playerResults.getPlayerResults(request.user.userPlayer)
    playerAccount = account.getAccount(request.user)
    playerCredits = credits.myCredits(request.user)
    creditsRecieved = transaction.getRecievedTransactions(playerAccount)
    creditsSpent = transaction.getPayedTransactions(playerAccount)
    userInfo = CustomUser.objects.filter(id = request.user.id)
    if request.method == 'POST':
        request.session['playerID'] = userInfo.id
        return redirect('playerEdit')
    else:
        return render(request, "player/playerActions.html",{
            "upcomingTournaments":upcomingTournaments, 
            "previousTournaments":previousTournaments,
            "creditsRecieved":creditsRecieved,
            "creditsSpent":creditsSpent,
            "userInfo":userInfo,
            "playerAccount":playerAccount,
            "playerCredits":playerCredits,
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
        return render(request, "proShop/purchaseFunds.html",{
            "form":form,
        })

@login_required
@user_passes_test(exec_test,login_url='/', redirect_field_name=None)
def execHome(request): 
    user = request.user
    curSection = user.execFields.section
    sectionCredits = credits.getSectionCredits(curSection)
    return render(request, "exec/execHome.html", {
        "sectionCredits":sectionCredits,
    })

@login_required
@user_passes_test(shop_test,login_url='/', redirect_field_name=None)
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
            billing_event = BillingEvent.initializeEvent(curPlayer,request.user,form.cleaned_data['Item_Description'],form.cleaned_data['Amount'])
            request.session['billingID'] = billing_event.BillingEventID
            return redirect('authorizeTransaction')
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
            return redirect('home')
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
@user_passes_test(shop_test,login_url='/', redirect_field_name=None)
def authorizeTransaction(request):
    curShop = request.user.userShop
    billingEvent = BillingEvent.objects.filter(BillingEventID=request.session['billingID'])[0]
    curPlayer = billingEvent.player_account.account_owner
    if request.method == 'POST':
        if request.POST['action'] == 'confirm':
            form = playerAuthPurchaseForm(request.POST)
            if form.is_valid():
                if player.checkPin(curPlayer,form.cleaned_data["Player_Pin"]):
                    BillingEvent.approveEvent(billingEvent)
                    del request.session['billingID']
                    credits.spendCredits(billingEvent.player_account,billingEvent.shop_account,billingEvent.amount, billingEvent.description)
                    return redirect('home')
                else:
                    missCounter = BillingEvent.authMiss(billingEvent)
                    messages.add_message(request,messages.WARNING,'Invalid PIN. %s attempts remaining.' % missCounter)
                    return render(request, 'proShop/authorizePurchase.html',{
                        'form':form,
                        'event':billingEvent,
                        'player':curPlayer,
                        'shop':curShop,
                    })
        else:
            BillingEvent.cancelEvent(billingEvent)
            return redirect('home')
    
    else: 
        form = playerAuthPurchaseForm()
        return render(request, 'proShop/authorizePurchase.html',{
            'form':form,
            'event':billingEvent,
            'player':curPlayer,
            'shop':curShop,
        })

@login_required
@user_passes_test(player_test)
def playerEdit(request):
    if request.session['playerID']:
        editUser = CustomUser.objects.filter(id=request.session['playerID'])[0]

    else:
        return redirect('home')