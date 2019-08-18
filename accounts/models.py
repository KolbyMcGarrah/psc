from django.db import models
from users.models import CustomUser, proShop, player, execUser
from datetime import datetime, date, timedelta
from django.db.models import Q
# Create your models here.
class account(models.Model):
    account_choices = ((1,'player'), (2,'shop'), (3,'buyer'), (4,'AmAd'))
    account_ID = models.AutoField(primary_key = True)
    current_balance = models.DecimalField(max_digits=11,decimal_places=2, blank=True, null=True, default = 0.00)
    last_updated = models.DateField(auto_now = True)
    account_created = models.DateField(auto_now_add = True)
    account_type = models.PositiveSmallIntegerField(
                    choices=account_choices,
                    default=1)
    account_owner = models.OneToOneField(CustomUser, related_name='userAccount', on_delete=models.CASCADE)
    stripe_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.account_owner) + " Account"
    
    def transferFunds(account1, account2, amount, reason):
        sourceAccount = account1
        destAccount = account2
        sourceBalance = sourceAccount.current_balance
        destBalance = destAccount.current_balance
        if sourceBalance >= amount: 
            newSourceBalance = sourceBalance - amount
            newdestBalance = destBalance + amount
            destAccount.current_balance = newdestBalance
            sourceAccount.current_balance = newSourceBalance
            destAccount.save()
            sourceAccount.save()
            credits.assignCredit(amount,sourceAccount,destAccount)
            transaction.log_transaction(sourceAccount, destAccount, amount, reason)
            return True
        else: 
            return False

    def addShopFunds(account1, amount):
        fundedAccount = account1.userAccount
        fundedAccount.current_balance += amount
        fundedAccount.save()
        AmAdUsr = CustomUser.objects.filter(username='AmAd')[0]
        transaction.log_transaction(AmAdUsr.userAccount,fundedAccount,amount,"Purchasing Credits")
    

    def createPlayerAccount(user):
        curAccount = account()
        curAccount.account_type = 1
        curAccount.current_balance = 0.00
        curAccount.account_owner=user
        return curAccount
    
    def createShopAccount(user): 
        curAccount = account()
        curAccount.account_type = 2
        curAccount.current_balance = 0.00
        curAccount.account_owner = user
        return curAccount
    
    def getAccount(user): 
        curAccount = account.objects.filter(account_owner = user)[0]
        return curAccount

    def getShopAccount(shop):
        shopAcct = account.getAccount(shop.user)
        return shopAcct

    def getPlayerAccount(player):
            return account.getAccount(player.user)
    def getTotalCredits(): 
        allAccounts = account.objects.all()
        accountTotal = 0.00
        for field in allAccounts:
            accountTotal = accountTotal + field.current_balance
        return accountTotal

    def fundsAvailable(curAccount, amount): 
        if curAccount.current_balance < amount: 
            return False
        else:
            return True

    def deductFunds(curAccount,shopAccount,amount,reason):
        if account.fundsAvailable(curAccount, amount):
            previousBalance = curAccount.current_balance
            newBalance = previousBalance - amount
            curAccount.current_balance = newBalance
            curAccount.save()
            transaction.log_transaction(curAccount,shopAccount,amount,reason)
            return True
        else:
            return False
   

    
class transaction(models.Model): 
    transaction_ID = models.AutoField(primary_key=True)
    source_account = models.ForeignKey(account, related_name='payedCredits', on_delete = models.CASCADE)
    destination_account = models.ForeignKey(account, related_name='recievedCredits', on_delete = models.CASCADE)
    amount = models.DecimalField(max_digits=11,decimal_places=2, blank=True, null=True, default = 0.00)
    transaction_date = models.DateField(auto_now = True)
    transaction_reason = models.CharField(max_length=1000)

    def log_transaction(account1, account2, amount, reason):
        newTransaction = transaction()
        newTransaction.source_account = account1
        newTransaction.destination_account = account2
        newTransaction.amount = amount
        newTransaction.transaction_reason = reason
        newTransaction.save()
    
    def getPayedTransactions(account1):
        transactions = account1.payedCredits.all()
        for field in transactions: 
           field.amount = (-1)*field.amount
        return transactions

    def getRecievedTransactions(account1):
        transactions = account1.recievedCredits.all()
        return transactions

class credits(models.Model): 
    status_choices = ((1,'Active'), (2,'Expiring'), (3,'Expired'))
    credit_id = models.AutoField(primary_key=True)
    credit_amount = models.DecimalField(max_digits=11, decimal_places=2, default=0.00)
    date_assigned = models.DateField(auto_now=True)
    expiration_date = models.DateField()
    status = models.PositiveSmallIntegerField(choices=status_choices,default=1)
    owner = models.ForeignKey(account,related_name="myCredits", on_delete=models.CASCADE, default=106)
    source = models.ForeignKey(account,related_name='accountCredits', on_delete=models.CASCADE)
    class Meta:
        verbose_name_plural = 'Credits'
    
    def __str__(self):
        return str(self.credit_amount) + ' credits for ' + str(self.owner)

    def assignCredit(amount,sourceAcct, destAccount): 
        credit = credits()
        credit.source = sourceAcct
        credit.owner = destAccount
        credit.expiration_date = date.today() + timedelta(days=60)
        credit.credit_amount=amount
        credit.save()
        return credit
    
    def myCredits(curUser): 
        return credits.objects.filter(owner=curUser.userAccount)
        
    def getSectionCredits(curSection):
        sectionCredits = credits.objects.filter(Q(source__account_owner__userShop__section = curSection)|Q(source__account_owner__execFields__section = curSection))
        return sectionCredits
    
    def spendCredits(source, destination, amount, reason):
        availableCredits = credits.objects.filter(owner=source).order_by('expiration_date')
        remainder = amount
        if account.deductFunds(source,destination,amount,reason):
            for credit in availableCredits:
                if remainder > 0:
                    remainder = remainder - credit.credit_amount
                    credit.credit_amount = (-1)*remainder
                    if credit.credit_amount <= 0:
                        credit.credit_amount = 0
                    credit.save()
                else:
                    pass                               
            credits.objects.filter(owner=source,credit_amount = 0).delete()
            return True
        else:
            return amount - source.current_balance
    
    def expireCredits():
        today = date.today()
        total_credits = credits.objects.filter(expiration_date__lt = today,status=2)
        for credit in total_credits:
            print("Updating: " + str(credit))
            credit.status = 3
            credit.save()

    def expiringCredits():
        exp_range = date.today() + timedelta(days=10)
        total_credits = credits.objects.filter(expiration_date__lt = exp_range, status=1)
        for credit in total_credits:
            print('Updating :' + str(credit))
            credit.status = 2
            credit.save()

    def totalSectionCredits(sec):
        secCredits = credits.getSectionCredits(sec)
        total = 0.00
        for credit in secCredits:
            total += float(credit.credit_amount)
        return total

    def activeSecCredits(sec):
        creditSet = credits.objects.filter(Q(source__account_owner__userShop__section = sec)|Q(source__account_owner__execFields__section = sec),status=1)
        total = 0.00
        for credit in creditSet:
            total += float(credit.credit_amount)
        return total    

    def expiringSecCredits(sec):
        creditSet = credits.objects.filter(Q(source__account_owner__userShop__section = sec)|Q(source__account_owner__execFields__section = sec),status=2)
        total = 0.00
        for credit in creditSet:
            total += float(credit.credit_amount)
        return total
    
    def expiredSecCredits(sec):
        creditSet = credits.objects.filter(Q(source__account_owner__userShop__section = sec)|Q(source__account_owner__execFields__section = sec),status=3)
        total = 0.00
        for credit in creditSet:
            total += float(credit.credit_amount)
        return total

class BillingEvent(models.Model):
    event_status = ((1,'pending'),(2,'not approved'),(3,'approved'),(4,'complete'))
    BillingEventID = models.AutoField(primary_key = True)
    amount = models.DecimalField(max_digits=11, decimal_places=2, default=0.00)
    description = models.CharField(max_length=1000)
    shop_account = models.ForeignKey(account,related_name='shopBillingEvents', on_delete=models.CASCADE)
    player_account = models.ForeignKey(account,related_name='playerBillingEvent', on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(choices=event_status,default=1)
    auth_attempt_counter = models.IntegerField(default=3)
    request_ts = models.DateField(auto_now_add = True)
    update_ts = models.DateField(auto_now = True)

    def __str__(self):
        return str(self.request_ts) + ' ' + str(self.shop_account) + ' ' + str(self.status) + ' Billing Event for ' + str(self.description)
    
    def initializeEvent(player, shop, desc, amt):
        newEvent = BillingEvent.objects.create(status=1,amount=amt,description=desc, player_account=player.userAccount, shop_account=shop.userAccount)
        return newEvent
    
    def approveEvent(event):
        event.status = 3
        event.save()
        return True

    def completeEvent(event):
        event.status = 4
        event.save()
        return True
    
    def cancelEvent(event):
        event.status = 2
        event.save()
        return True

    def getEvents(shop):
        return shop.userAccount.shopBillingEvents
    
    def getPendingEvents(shop):
        return BillingEvent.objects.filter(shop_account=shop.userAccount, status = 1)
    
    def getCompleteEvents(shop):
        return BillingEvent.objects.filter(shop_account=shop.userAccount, status = 4)
    
    def getApprovedEvents(shop):
        return BillingEvent.objects.filter(shop_account=shop.userAccount, status = 3)
    
    def authMiss(event):
        missCounter = event.auth_attempt_counter
        missCounter = missCounter - 1
        event.auth_attempt_counter = missCounter
        event.save()
        return missCounter
    
    def getEventByID(eventID):
        return BillingEvent.objects.get(BillingEventID=eventID)



                    
