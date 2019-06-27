from django.shortcuts import render, redirect
from .forms import eventScheduleForm, searchPlayer, resultsForm, resultFormSet
from .models import PGA_Event as pg, results as res
from users.models import CustomUser as cu, player as ply, proShop as ps, execUser as eu
from django.shortcuts import get_object_or_404
import re

# Create your views here.
def schedule(request):
    if request.method == "POST":
        form = eventScheduleForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['event_name']
            eDate = form.cleaned_data['event_date']
            numPlayer = form.cleaned_data['number_of_players']
            prize = form.cleaned_data['prize_pool']
            host = form.cleaned_data['host_shop']
            sec = request.user.execFields
            event_id = pg.scheduleEvent(name,sec,numPlayer,eDate,host,prize)
            request.session['event_id'] = event_id
        return redirect('update')
    else:
        eventForm = eventScheduleForm()
        return render(request,'events/schedule.html',{
            "form":eventForm,
        })

def update(request):
    if request.session['event_id']:
        event_id = request.session['event_id']
    curEvent = get_object_or_404(pg, event_id = event_id)
    if curEvent.status == '3':
        return redirect("setResults")
    playerResults = res.getEventPlayers(curEvent)
    if request.method == 'POST':
        postRequest = request.POST['action']
        if 'add' in postRequest:
            playerID = re.match(r"add(.*)", postRequest)
            res.addPlayer(playerID.group(1),curEvent)
            playerResults = res.getEventPlayers(curEvent)
            searchForm = searchPlayer()
            return render(request,'events/update.html',{
                'playerResults':playerResults,
                'searchForm':searchForm,
                'Event':curEvent,
            })
        elif postRequest == 'Search':
            search = searchPlayer(request.POST)
            if search.is_valid():
                first = search.cleaned_data['First_Name']
                last = search.cleaned_data['Last_Name'] 
                results = ply.searchPlayer(first,last)
            return render(request,'events/update.html',{
                'results':results,
                'Event':curEvent,                
                'playerResults':playerResults,
            })
        elif 'remove' in postRequest:
            playerID = re.match(r"remove(.*)", postRequest)
            res.removePlayer(playerID.group(1),curEvent)
            playerResults = res.getEventPlayers(curEvent)
            searchForm = searchPlayer()
            return render(request,'events/update.html',{
                'playerResults':playerResults,
                'searchForm':searchForm,
                'Event':curEvent,
            })
        elif postRequest == 'finalize':
            pg.finalizeRoster(curEvent)
            return redirect('setResults')        
    else:
        searchForm = searchPlayer()
        return render(request, 'events/update.html',{
            'searchForm':searchForm,
            'Event': curEvent,
            'playerResults':playerResults,
        })

def setResults(request):
    if request.session['event_id']:
        event_id = request.session['event_id']
    curEvent = get_object_or_404(pg, event_id = event_id)
    eventPlayers = res.getEventPlayers(curEvent)
    if request.method == 'POST':
        formset = resultFormSet(request.POST,request.FILES)
        for form in formset:
            if form.is_valid():
                form.save()
        actual = res.calcPrizePool(curEvent)
        if float(actual) != float(curEvent.prize_pool):
            request.session['prize'] = actual
            return redirect("confirmPrize")
        else:
            return redirect("purchaseCredits")
    else:    
        formset = resultFormSet(queryset=eventPlayers)
        return render(request,'events/setResults.html',{
            'eventPlayers':eventPlayers,
            'formset':formset,
            'curEvent':curEvent,
        })

def confirmPrize(request):
    if request.session['event_id']:
        event_id = request.session['event_id']
    curEvent = get_object_or_404(pg, event_id = event_id)
    if request.session['prize']:
        amount = request.session['prize']
    else:
        amount = res.calcPrizePool(curEvent)
    estimate = curEvent.prize_pool
    if request.method == 'POST':
        requestEvent = request.POST['action']
        if requestEvent == 'Confirm':
            curEvent.prize_pool = amount
            curEvent.save()
            return redirect('purchaseCredits')
        else:
            return redirect('setResults')
    else:
        return render(request, 'events/confirmPrize.html',{
            'amount':amount,
            'estimate':estimate,
        })