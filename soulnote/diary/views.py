# Views in Django handle the request and return a response 
# (similar to Flask route functions decorated with @app.route)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import DiaryEntry
from .forms import DiaryEntryForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Automatically log the user in right after registration
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    
    return render(request, 'diary/register.html', {'form': form})

@login_required(login_url='/login/')
def home_view(request):
    if request.method == 'POST':
        form = DiaryEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False) # Don't save to DB yet; we need to attach user and IP
            entry.user = request.user      # Attach the currently logged-in user
            
            # Capture IP address for forensic/audit logging
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                entry.ip_address = x_forwarded_for.split(',')[0]
            else:
                entry.ip_address = request.META.get('REMOTE_ADDR')
                
            entry.save()
            return redirect('home')
    else:
        form = DiaryEntryForm()

    # Security check: Filter entries strictly by the logged-in user
    entries = DiaryEntry.objects.filter(user=request.user)
    
    context = {
        'form': form,
        'entries': entries,
    }
    return render(request, 'diary/home.html', context)
