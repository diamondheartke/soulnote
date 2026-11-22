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
			login(request, user)
			
			request.session['username'] = user.username
			return redirect('home')
	else:
		form = UserCreationForm()
	
	return render(request, 'diary/register.html', {'form': form})
	
@login_required(login_url='/login/')
def landing_view(request):
	if request.user.is_authenticated:
		return redirect('home')
	return render(request, 'diary/landing.html')

@login_required(login_url='/login/')
def diary_view(request):
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
			return redirect('diary-space')
	else:
		form = DiaryEntryForm()

	# Security check: Filter entries strictly by the logged-in user
	entries = DiaryEntry.objects.filter(user=request.user)
	
	context = {
		'form': form,
		'entries': entries,
	}
	return render(request, 'diary/diary-space.html', context)

@login_required(login_url='/login/')
def home_view(request):
	from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import DiaryEntry
from .forms import DiaryEntryForm


def register_view(request):
	if request.method == 'POST':
		form = UserCreationForm(request.POST)

		if form.is_valid():
			user = form.save()
			login(request, user)

			request.session['username'] = user.username

			return redirect('home')
	else:
		form = UserCreationForm()

	return render(request, 'diary/register.html', {'form': form})


def landing_view(request):
	if request.user.is_authenticated:
		return redirect('home')

	return render(request, 'diary/landing.html')


@login_required(login_url='landing')
def home_view(request):

	entries = DiaryEntry.objects.filter(
		user=request.user
	).order_by('-id')

	context = {
		'username': request.user.username,
		'entries': entries,
		'entry_count': entries.count(),
	}

	return render(request, 'diary/home.html', context)


@login_required(login_url='landing')
def diary_view(request):
    if request.method == 'POST':
        form = DiaryEntryForm(request.POST)

        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user

            x_forwarded_for = request.META.get(
                'HTTP_X_FORWARDED_FOR'
            )

            if x_forwarded_for:
                entry.ip_address = x_forwarded_for.split(',')[0].strip()
            else:
                entry.ip_address = request.META.get('REMOTE_ADDR')

            entry.save()

            return redirect('diary-space')

    else:
        form = DiaryEntryForm()

    entries = DiaryEntry.objects.filter(
        user=request.user
    ).order_by('-id')

    context = {
        'form': form,
        'entries': entries,
    }

    return render(request, 'diary/diary-space.html', context)
