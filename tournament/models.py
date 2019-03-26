from django.db import models
from users.models import player, proShop

# Create your models here.
class tournament (models.Model):
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
    active = models.BooleanField(default = True)
    def __str__(self):
        return self.tournament_name + ' ' + str(self.shop) + ' ' + str(self.tournament_id)
    def getTournamentFromID(id):
        return tournament.objects.filter(tournament_id = id)[0]

class playerResults (models.Model): 
    tournament = models.ForeignKey(tournament, related_name = 'tournamentSet',on_delete=models.CASCADE)
    player = models.ForeignKey(player, related_name='tournamentPlayer', on_delete=models.CASCADE)
    amount_won = models.DecimalField(max_digits=11,decimal_places=2, blank=True, null=True, default = 0.00)
    position = models.PositiveIntegerField(blank=True, null=True, default = '0')
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
    


