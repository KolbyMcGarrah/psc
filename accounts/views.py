from django.shortcuts import render, redirect
from .models import account, transaction
from users.forms import purchaseForm
from django.conf import settings
from decimal import Decimal
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

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

def successfulTransaction(request):
    return render(request,'account/successfulTransaction.html')

def failedTransaction(request):
    transError = request.session['transError']
    context = {"error":transError}
    return render(request,'account/failedTransaction.html',{
        "error": context,
    })