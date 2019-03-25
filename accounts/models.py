from django.db import models
from users.models import CustomUser

# Create your models here.
class account(models.Model):
    account_choices = ((1,'player'), (2,'shop'), (3,'buyer'))
    account_ID = models.AutoField(primary_key = True)
    current_balance = models.DecimalField(max_digits=11,decimal_places=2, blank=True, null=True, default = 0.00)
    last_updated = models.DateField(auto_now = True)
    account_created = models.DateField(auto_now_add = True)
    account_type = models.PositiveSmallIntegerField(
                    choices=account_choices,
                    default=1)
    account_owner = models.OneToOneField(CustomUser, related_name='userAccount', on_delete=models.CASCADE)
    
    def deduct(amount, balance): 
        result = balance-amount
        if(result < 0.00): 
            return "Insufficient Funds"
        else:
            return result

    def add(amount, balance): 
        return (amount + balance)

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
    
    def getTotalCredits(): 
        allAccounts = account.objects.all()
        accountTotal = 0.00
        for field in allAccounts:
            accountTotal = accountTotal + field.current_balance
        return accountTotal


    
class transaction(models.Model): 
    transaction_ID = models.AutoField(primary_key=True)
    source_account = models.PositiveIntegerField(null=False)
    destination_account = models.PositiveIntegerField(null=False)
    amount = models.DecimalField(max_digits=11,decimal_places=2, blank=True, null=True, default = 0.00)
    transaction_date = models.DateField(auto_now = True)
    transaction_reason = models.CharField(max_length=1000)
