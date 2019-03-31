from django.db import models
from users.models import CustomUser

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

    def __str__(self):
        return str(self.account_owner) + " Account"
    
    def transferFunds(account1, account2, amount, reason):
        sourceAccount = account1.userAccount
        destAccount = account2.userAccount
        sourceBalance = sourceAccount.current_balance
        destBalance = destAccount.current_balance
        if sourceBalance > amount: 
            newSourceBalance = sourceBalance - amount
            newdestBalance = destBalance + amount
            destAccount.current_balance = newdestBalance
            sourceAccount.current_balance = newSourceBalance
            destAccount.save()
            sourceAccount.save()
            transaction.log_transaction(sourceAccount, destAccount, amount, reason)
            return True
        else: 
            return False

    def addShopFunds(account1, amount):
        fundedAccount = account1.userAccount
        fundedAccount.current_balance += amount
        fundedAccount.save()
        AmAdUsr = CustomUser.objects.filter(username='AmAd')[0]
        transaction.log_transaction(AmAdUsr.userAccount,fundedAccount,amount,"Adding purchased credits to the pro shop account")
         

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
           field.amount = (-1)*amount
        return transactions

    def getRecievedTransactions(account1):
        transactions = account1.recievedCredits.all()
        return transactions
