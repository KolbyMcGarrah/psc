from django.shortcuts import render, redirect
from accounts.models import account, transaction, credits, BillingEvent
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import CustomUser, proShop, player, execUser
from django.conf import settings
from .forms import *
import urllib


def shop_test(user):
    return CustomUser.isShop(user)

def player_test(user):
    return CustomUser.isPlayer(user)

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
        return render(request, "proshop/spendCredits.html",{
            "playerCredits":playerCredits,
            "shop":curShop,
            "player":curPlayer,
            "playerAccount":playerAccount,
            "form":form,
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
                    return render(request, 'proshop/authorizePurchase.html',{
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
        return render(request, 'proshop/authorizePurchase.html',{
            'form':form,
            'event':billingEvent,
            'player':curPlayer,
            'shop':curShop,
        })

@login_required
@user_passes_test(shop_test,login_url='/', redirect_field_name=None)
def billing(request):
    curShop = request.user.userShop
    shopAct = account.getShopAccount(curShop)
    if shopAct.stripe_id is None:
        redirectURL=settings.STRIPE_REDIRECT
        url = f'https://connect.stripe.com/oauth/authorize'
        params = {
            'response_type': 'code',
            'client_id':settings.STRIPE_CLIENT_ID,
            'redirect_uri':redirectURL, 
            'scope':'read-write',
        }
        #Redirect to stripe connect page.
        url = f'{url}?{urllib.parse.urlencode(params)}'
        return redirect(url)
    else:
        print(shopAct.stripe_id)
        return redirect(home)

def stripeConfirm(request):
    curShop = users.getShopFromID(id)
    shopAct = accounts.getShopAccount(curShop)
    code = request.GET.get('code')
    if code:
        data = {
            'client_secret': settings.STRIPE_SECRET_KEY,
            'grant_type': 'authorization_code',
            'client_id': settings.STRIPE_CLIENT_ID,
            'code': code
        }
        url = 'https://connect.stripe.com/oauth/token'
        resp = requests.post(url, params=data)
        print(resp.json)
        stripe_user_id = resp.json()['stripe_user_id']
        stripe_access_token = resp.json()['access_token']
        shopAct.stripe_id = stripe_user_id
        shopAct.stripe_access_token = stripe_access_token
        shopAct.save()
        return redirect(billing)
