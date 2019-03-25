from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomUserManager(UserManager):
    pass

class CustomUser(AbstractUser):
    user_choices = ((1,'admin'), (2,'player'), (3,'shop'), (4,'buyer'))
    objects = CustomUserManager()
    userType = models.PositiveSmallIntegerField(
                  choices=user_choices,
                  default=1)
    phoneNumber = models.CharField(max_length = 10, null=True)

class player (models.Model):
    user = models.OneToOneField(CustomUser, related_name='userPlayer', on_delete=models.CASCADE, primary_key = True)
    address = models.CharField(max_length = 50)
    homeCourse = models.CharField(max_length = 50)
    insrt_timestamp = models.DateField(auto_now_add = True)
    chnge_timestamp = models.DateField(auto_now = True)
    def __str__(self):
        return str(self.user)

class proShop (models.Model):
    user = models.OneToOneField(CustomUser, related_name='userShop', on_delete=models.CASCADE, primary_key = True)
    shop_name = models.CharField(max_length = 50)
    head_pro = models.CharField(max_length = 50)
    assistant_pro = models.CharField(max_length = 10)
    shop_adress = models.CharField(max_length = 50)
    pga_number = models.IntegerField(null=True)
    insrt_timestamp = models.DateField(auto_now_add = True)
    chnge_timestamp = models.DateField(auto_now = True)
    def __str__(self):
        return self.shop_name
        
    

