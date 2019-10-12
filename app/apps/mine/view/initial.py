from django.shortcuts import redirect, render

def initial(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='miner').exists():
            return redirect('mine:miner-initial')
        else:
            return redirect('mine:moderator-initial')
    return render(request, 'authentication/initial.html')