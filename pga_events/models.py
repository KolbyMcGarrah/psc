from django.db import models
from users.models import player, execUser, CustomUser, proShop
from accounts.models import *
from django.db.models import Q

# Create your models here.
class PGA_Event (models.Model):
    user_choices = ((1,'active'), (2,'abandoned'), (3,'started'), (4,'complete'))
    event_id = models.AutoField(primary_key = True)
    event_name = models.CharField(max_length = 50) 
    Section = models.ForeignKey(execUser, related_name='Section', on_delete=models.CASCADE)
    players = models.ManyToManyField(
        player, 
        through='results', 
        through_fields=('PGA_Event','player')
        )
    number_of_players = models.PositiveIntegerField(null=True, default=0)
    created_on = models.DateField(auto_now_add = True)
    last_updated = models.DateField(auto_now = True)
    event_date = models.DateField()
    prize_pool = models.DecimalField(max_digits=11,decimal_places=2, blank=True, null=True, default = 0.00)
    host_shop = models.ForeignKey(proShop, related_name='host',on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(
                  choices=user_choices,
                  default=1)
    class Meta:
        verbose_name_plural = "PGA Events"
    
    def __str__(self):
        event = str(self.event_name) + ' for ' + str(self.Section) + ' hosted at ' + str(self.host_shop)
        return event

    def scheduleEvent(name,sec,numPlayer,eDate,host,prize):
        newEvent = PGA_Event()
        newEvent.event_name = name
        newEvent.Section = sec
        newEvent.number_of_players = numPlayer
        newEvent.event_date = eDate
        newEvent.host_shop = host
        newEvent.prize_pool = prize
        newEvent.save()
        return newEvent.event_id
    
    def upcomingEvents(section):
        return PGA_Event.objects.filter(Q(status = 1) | Q(status = 3),Section = section )
    
    def pastEvents(section):
        return PGA_Event.objects.filter(Q(status = 2) | Q(status = 4),Section = section )
    
    def removeEvent(eventID):
        PGA_Event.objects.get(event_id = eventID).delete()
    
    def finalizeRoster(event):
        event.status = 3
        event.save()

class results (models.Model):
    flight_choices = ((1,'Flight 1'), (2,'Flight 2'), (3,'Flight 3'), (4,'Flight 4'), (5,'Flight 5'), (6,'Flight 6'), (7,'Flight 7'), (8,'Flight 8'),
                     (9,'Flight 9'), (10,'Flight 10'))
    division_choices = ((1,'Senior'), (2,'Women'), (3,'Junior'),(4,'Men'))
    PGA_Event = models.ForeignKey(PGA_Event, related_name = 'eventSet',on_delete=models.CASCADE)
    player = models.ForeignKey(player, related_name='eventPlayer', on_delete=models.CASCADE)
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
        verbose_name_plural = "Results"
    
    def addPlayer(playerID,event):
        pler = player.getPlayerFromID(playerID)
        existing = results.objects.filter(PGA_Event = event, player = pler)
        if not existing:
            newPlayer = results()
            newPlayer.PGA_Event = event
            newPlayer.player = pler
            newPlayer.save()
    
    def finalizeEvent(pResults, event):
        results.assign_Results(pResults, event)
        event.status = 4
        event.save()
    
    def assign_Results(pResults,event):
        for field in pResults: 
            winnings = field.amount_won
            reasonCode = str(event.event_name) + ' winnings'
            sourceAccount = event.Section.user.userAccount
            playerAccount = account.getPlayerAccount(field.player)
            account.transferFunds(sourceAccount,playerAccount,winnings,reasonCode)
    
    def getEventPlayers(event):
        return results.objects.filter(PGA_Event=event)

    def removePlayer(playerID, event):
        remPlayer = player.getPlayerFromID(playerID)
        if remPlayer:
            results.objects.get(player=remPlayer, PGA_Event=event).delete()
    
    def calcPrizePool(curEvent):
        resultSet = results.getEventPlayers(curEvent)
        actual = 0.0
        for result in resultSet:
            actual += float(result.amount_won)
        return actual

    def getWinningPlayers(event):
        resultSet = results.getEventPlayers(event)
        winningPlayers = []
        for result in resultSet:
            if result.amount_won > 0:
                winningPlayers.append(result)
        return winningPlayers
        
        