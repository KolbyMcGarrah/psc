from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import account, transaction
from users.forms import purchaseForm
from users.models import CustomUser
from django.conf import settings
from decimal import Decimal
from django.shortcuts import get_object_or_404
from pga_events.models import PGA_Event as pg, results as res
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY
client_id = settings.STRIPE_CLIENT_ID

def shop_test(user):
    return CustomUser.isShop(user)

@login_required
def payment(request):
    curShop = request.user
    if request.method == "POST":
        form = purchaseForm(request.POST)
        if form.is_valid():
            amount = request.POST['amount']
            adjustedAmount = 100*float(amount)
            token = request.POST['stripeToken']
            try:
                charge = stripe.Charge.create(
                amount= int(adjustedAmount),
                currency='usd',
                description='Purchasing Credits',
                source=token
                )
                account.addShopFunds(curShop,Decimal(amount)) 
                return redirect("successfulTransaction")
            except stripe.error.CardError as e:
                body = e.json_body
                err  = body.get('error', {})
                request.session['transError'] = err.get('message')
                return redirect("failedTransaction") 
    else: 
        form = purchaseForm()
        return render(request, "account/purchaseFunds.html",{
            "form":form,
        })
@login_required
def successfulTransaction(request):
    return render(request,'account/successfulTransaction.html')
    
@login_required
def failedTransaction(request):
    transError = request.session['transError']
    context = {"error":transError}
    return render(request,'account/failedTransaction.html',{
        "error": context,
    })

def purchaseCredits(request):
    if request.session['event_id']:
        event_id = request.session['event_id']
    user = request.user
    curEvent = get_object_or_404(pg,event_id = event_id)
    resultSet = res.getWinningPlayers(curEvent)
    amount = curEvent.prize_pool
    if request.method == "POST":
        adjustedAmount = 100*float(amount)
        token = request.POST['stripeToken']
        try:
            charge = stripe.Charge.create(
            amount= int(adjustedAmount),
            currency='usd',
            description='Purchasing Credits',
            source=token
            )
            account.addShopFunds(user,Decimal(amount))
            res.finalizeEvent(resultSet,curEvent)
            return redirect("successfulTransaction")
        except stripe.error.CardError as e:
            body = e.json_body
            err  = body.get('error', {})
            request.session['transError'] = err.get('message')
            return redirect("failedTransaction") 
    else: 
        form = purchaseForm()
        return render(request, "account/purchaseCredits.html",{
            "amount":amount,
        })

def connectStripe(request):
    return render(request, "account/connectStripe.html")

def completeEvents(request):
    user = request.user
    return render(request, "account/completeEvents")