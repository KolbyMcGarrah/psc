from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from passlib.hash import pbkdf2_sha256

class CustomUserManager(UserManager):
    pass

class CustomUser(AbstractUser):
    user_choices = ((1,'admin'), (2,'player'), (3,'shop'), (4,'buyer'), (5, 'exec'))
    objects = CustomUserManager()
    userType = models.PositiveSmallIntegerField(
                  choices=user_choices,
                  default=1)
    phoneNumber = models.CharField(max_length = 10, null=True)

    def isPlayer(user):
        if user.userType == 2:
            return True
        else:
            return False

    def isShop(user):
        if user.userType == 3:
            return True
        else:
            return False

    def isExec(user):
        if user.userType == 5:
            return True
        else:
            return False

class player (models.Model):
    #golf_level_choices = ((1,'pro'), (2,'amature'))
    user = models.OneToOneField(CustomUser, related_name='userPlayer', on_delete=models.CASCADE, primary_key = True)
    address = models.CharField(max_length = 50)
    homeCourse = models.CharField(max_length = 50)
    #golf_level = models.PositiveSmallIntegerField(
    #               choices=golf_level_choices
    #               default=2)
    insrt_timestamp = models.DateField(auto_now_add = True)
    chnge_timestamp = models.DateField(auto_now = True)
    pin = models.CharField(max_length=128, default='0000')

    def __str__(self):
        return str(self.user)

    def updatePin(newUser, Pin):
        updatePlayer = newUser.userPlayer
        updatePlayer.pin = pbkdf2_sha256.encrypt(Pin,rounds=120000,salt_size=32)
        updatePlayer.save()

    def checkPin(player, Pin):
        curPlayer = player.userPlayer
        playerPIN = curPlayer.pin
        return pbkdf2_sha256.verify(Pin, playerPIN)

    def searchPlayer(first,last):
        if first and last:
            playerSet = player.objects.filter(user__first_name__icontains = first, user__last_name__icontains = last, user__userType=2)
        elif first:
            playerSet = player.objects.filter(user__first_name__icontains = first, user__userType=2)
        elif last:
            playerSet = player.objects.filter(user__last_name__icontains = last, user__userType=2)
        else:
            playerSet = player.objects.all()
        return playerSet

    def getPlayerFromID(id):
        return player.objects.get(user__id = id)

class proShop (models.Model):
    section_options = ((1,'Alabama'),(2,'Colorado'),(3,'Carolinas'),(4,'Georgia'),(5,'Central New York'),(6,'Illinois'),(7,'Connecticut'),(8,'Iowa'),(9,'Gateway'),(10,'Metropolitan NY'),
                        (11,'Gulf States'),(12,'Middle Atlantic'),(13,'Indiana'),(14,'Minnesota'),(15,'Kentucky'),(16,'New England'),(17,'Michigan'),(18,'North Florida'),(19,'Midwest'),(20,'Northern California'),
                        (21,'Nebraska'),(22,'Northern Texas'),(23,'New Jersey'),(24,'Philadelphia'),(25,'Northeastern New York'),(26,'South Central'),(27,'Northern Ohio'),(28,'Southern California'),(29,'Pacific Northwest'),(30,'Southern Texas'),
                        (31,'Rocky Mountain'),(32,'Sun County'),(33,'South Florida'),(34,'Southern Ohio'),(35,'Tri-State'),(36,'Southwest'),(37,'Western New York'),(38,'Tennessee'),(39,'Utah'),(40,'Wisconsin'),(41,'Aloha'))
    user = models.OneToOneField(CustomUser, related_name='userShop', on_delete=models.CASCADE, primary_key = True)
    shop_name = models.CharField(max_length = 50)
    head_pro = models.CharField(max_length = 50)
    assistant_pro = models.CharField(max_length = 10)
    shop_adress = models.CharField(max_length = 50)
    pga_number = models.IntegerField(null=True)
    section = models.PositiveSmallIntegerField(
                  choices=section_options,
                  default=1)
    insrt_timestamp = models.DateField(auto_now_add = True)
    chnge_timestamp = models.DateField(auto_now = True)
    def __str__(self):
        return self.shop_name

    def getSectionShops(sec):
        return proShop.objects.filter(section=sec)

    def getShopFromID(id):
        return proShop.objects.get(user__id = id)

class execUser(models.Model):
    section_options = ((1,'Alabama'),(2,'Colorado'),(3,'Carolinas'),(4,'Georgia'),(5,'Central New York'),(6,'Illinois'),(7,'Connecticut'),(8,'Iowa'),(9,'Gateway'),(10,'Metropolitan NY'),
                        (11,'Gulf States'),(12,'Middle Atlantic'),(13,'Indiana'),(14,'Minnesota'),(15,'Kentucky'),(16,'New England'),(17,'Michigan'),(18,'North Florida'),(19,'Midwest'),(20,'Northern California'),
                        (21,'Nebraska'),(22,'Northern Texas'),(23,'New Jersey'),(24,'Philadelphia'),(25,'Northeastern New York'),(26,'South Central'),(27,'Northern Ohio'),(28,'Southern California'),(29,'Pacific Northwest'),(30,'Southern Texas'),
                        (31,'Rocky Mountain'),(32,'Sun County'),(33,'South Florida'),(34,'Southern Ohio'),(35,'Tri-State'),(36,'Southwest'),(37,'Western New York'),(38,'Tennessee'),(39,'Utah'),(40,'Wisconsin'),(41,'Aloha'))
    user = models.OneToOneField(CustomUser, related_name='execFields', on_delete=models.CASCADE, primary_key = True)
    insrt_timestamp = models.DateField(auto_now_add=True)
    chnge_timestamp = models.DateField(auto_now = True)
    section = models.PositiveSmallIntegerField(
                  choices=section_options,
                  default=1)

    def __str__(self):
        return self.user.username
