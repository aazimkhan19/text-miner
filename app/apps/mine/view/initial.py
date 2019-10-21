from django.shortcuts import redirect, render

def initial(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='miner').exists():
            return redirect('mine:miner-initial')
        else:
            return redirect('mine:moderator-initial')
    return render(request, 'authentication/initial.html')


def error404(request, exception):
    return render(request, 'mine/404.html', status=404)


def error500(request):
    return render(request, 'mine/500.html', status=500)