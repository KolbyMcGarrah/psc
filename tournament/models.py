from django.db import models
from users.models import player, proShop, execUser
from accounts.models import account, transaction

# Create your models here.
class tournament (models.Model):
    user_choices = ((1,'active'), (2,'abandoned'), (3,'in_progress'), (4,'complete'))
    tournament_id = models.AutoField(primary_key = True)
    tournament_name = models.CharField(max_length = 50) 
    shop = models.ForeignKey(proShop, related_name='shopTournament', on_delete=models.CASCADE)
    players = models.ManyToManyField(
        player, 
        through='playerResults', 
        through_fields=('tournament','player')
        )
    number_of_players = models.PositiveIntegerField(null=True, default=0)
    created_on = models.DateField(auto_now_add = True)
    last_updated = models.DateField(auto_now = True)
    tournament_date = models.DateField()
    prize_pool = models.DecimalField(max_digits=11,decimal_places=2, blank=True, null=True, default = 0.00)
    status = models.PositiveSmallIntegerField(
                  choices=user_choices,
                  default=1)
    def __str__(self):
        return self.tournament_name + ' ' + str(self.shop) + ' ' + str(self.tournament_id)
    def getTournamentFromID(id):
        return tournament.objects.filter(tournament_id = id)[0]
    
    def getActiveTournaments(curShop): 
        tournamentSet = []
        activeTournaments = tournament.objects.filter(shop=curShop, status=1)
        inprogTournaments = tournament.objects.filter(shop=curShop, status=3)
        for tourn in inprogTournaments:
            tournamentSet.append(tourn)
        for tourn in activeTournaments:
            tournamentSet.append(tourn)
        return tournamentSet

    def balanceWinnings(curTourn, amountsAwarded):
        prizePool = curTourn.prize_pool
        totalAmt = amountsAwarded
        print('attempting this')
        print(totalAmt)
        print(prizePool)
        if prizePool == totalAmt:
            print('Exact')
            return "Exact"
        elif prizePool < totalAmt:
            return "Over"
        else:
            return "Under"
    
    def assign_Results(pResults,curTournament):
        for field in pResults: 
            winnings = field.amount_won
            reasonCode = str(curTournament.tournament_name) + ' winnings'
            sourceAccount = account.getShopAccount(curTournament.shop)
            playerAccount = account.getPlayerAccount(field.player)
            account.transferFunds(sourceAccount,playerAccount,winnings,reasonCode)
    
    def finalizeTournament(pResults, curTournament):
        #check if the tournament has enough credits to back the transaction
        if account.fundsAvailable(curTournament.shop.user.userAccount, curTournament.prize_pool):
            tournament.assign_Results(pResults, curTournament)
            curTournament.status = 4
            curTournament.save()
            return 'Success'
        else:
            return 'Purchase Funds'
    
    def shopTournCount(curShop):
        return tournament.objects.filter(shop = curShop).count()
    
    def zipShopInfo(shopSet):
        zipped = {}
        for curShop in shopSet:
            zipped[str(curShop.shop_name)] = tournament.shopTournCount(curShop)
        return zipped

    def getMostActiveShops(sec, limit):
        secShops = proShop.getSectionShops(sec)
        unsorted = tournament.zipShopInfo(secShops)
        sorted_shops = sorted(unsorted.items(), key=lambda kv: kv[1], reverse = True)
        if limit < len(sorted_shops):
            limit = len(sorted_shops)
        return sorted_shops[:limit]
    
    def getLeastActiveShops(sec, limit):
        secShops = proShop.getSectionShops(sec)
        unsorted = tournament.zipShopInfo(secShops)
        sorted_shops = sorted(unsorted.items(), key=lambda kv: kv[1],reverse=False)
        if limit < len(sorted_shops):
            limit = len(sorted_shops)
        return sorted_shops[:limit -1]

        
class playerResults (models.Model): 
    flight_choices = ((1,'Flight 1'), (2,'Flight 2'), (3,'Flight 3'), (4,'Flight 4'), (5,'Flight 5'), (6,'Flight 6'), (7,'Flight 7'), (8,'Flight 8'),
                     (9,'Flight 9'), (10,'Flight 10'))
    division_choices = ((1,'Senior'), (2,'Women'), (3,'Junior'),(4,'Men'))
    tournament = models.ForeignKey(tournament, related_name = 'tournamentSet',on_delete=models.CASCADE)
    player = models.ForeignKey(player, related_name='tournamentPlayer', on_delete=models.CASCADE)
    amount_won = models.DecimalField(max_digits=11,decimal_places=2, blank=True, null=True, default = 0.00)
    position = models.PositiveIntegerField(blank=True, null=True, default = '0')
    flight = models.PositiveSmallIntegerField(
                  choices=flight_choices,
                  default=1)
    division = models.PositiveSmallIntegerField(
                  choices=division_choices,
                  default=1)
    added_on = models.DateField(auto_now_add = True)
    class Meta:
        verbose_name_plural = 'playerResults'
    
    def __str__(self):
        return str(self.tournament.shop) + ' ' + str(self.tournament.tournament_name) + str(self.tournament.tournament_id) + ' ' + str(self.player)
    
    def getTournamentPlayers(tourn):
        return playerResults.objects.filter(tournament = tourn)

    def setAmount(amount, curPlayer):
        current = playerResults.objects.filter(player = curPlayer)[0]
        current.amount_won = amount
        current.save()
    
    def setPosition(pos, curPlayer):
        current = playerResults.objects.filter(player = curPlayer)[0]
        current.position = pos
        current.save()
    def getPlayerResults(curPlayer):
        results = []
        allResults = playerResults.objects.filter(player=curPlayer)
        for field in allResults:
            if field.tournament.status == 4:
                results.append(field)
        return results

