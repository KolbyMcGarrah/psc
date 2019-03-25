from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.views import View
from users.models import *

class HomePageView(View):
    def get(self, request):    
        if request.user.is_authenticated:
            userType = CustomUser.objects.values('userType').get(id=request.user.id)
            print(userType)
            if userType['userType'] == 2:
                return redirect('users/playerActions')
            elif userType['userType'] == 3:
                return redirect('users/shopActions')
            else:
                return render('home.html')
        else:
            return render(request,'home.html')
