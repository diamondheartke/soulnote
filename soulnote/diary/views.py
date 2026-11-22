# Views in Django handle the request and return a response 
# (similar to Flask route functions decorated with @app.route)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, DiaryEntryForm
from django.contrib.auth import login
from .models import DiaryEntry

# delete account operations
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

@login_required(login_url='landing')
@require_http_methods(["GET", "POST"])
def delete_account_view(request):

	if request.method == 'POST':
		password = request.POST.get('password', '')
		confirmation = request.POST.get('confirmation', '')

		if not request.user.check_password(password):
			return render(request, 'diary/delete-account.html', {
				'error': 'The password you entered is incorrect.'
			})

		if confirmation != 'DELETE':
			return render(request, 'diary/delete-account.html', {
				'error': 'Please type DELETE exactly to confirm.'
			})

		# Keep a reference to the user before deleting the account.
		user = request.user

		# Delete the account and related diary entries.
		user.delete()

		# Clear the authenticated session.
		logout(request)

		return redirect('landing')

	return render(request, 'diary/delete-account.html')
	
# Export operations
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET

import uuid



@login_required(login_url='landing')
@require_GET
def export_data_view(request):
    user = request.user

    entries = DiaryEntry.objects.filter(
        user=user
    ).order_by('created_at', 'id')

    export_data = {
        "format": "SoulNote Data Export",
        "schema_version": "1.0",
        "exported_at": timezone.now().isoformat(),

        "profile": {
            "username": user.username,
            "profile_name": user.first_name,
            "email": user.email,
            "date_joined": user.date_joined.isoformat(),
        },

        "diary_entries": [
            {
                "entry_uuid": str(entry.entry_uuid),
                "id": entry.id,
                "content": entry.content,
                "detected_emotions": entry.detected_emotions,
                "ai_reflection": entry.ai_reflection,
                "ip_address": entry.ip_address,
                "created_at": entry.created_at.isoformat(),
                "updated_at": entry.updated_at.isoformat(),
            }
            for entry in entries
        ],

        "metadata": {
            "total_entries": entries.count(),
            "application": "SoulNote",
        },
    }

    response = JsonResponse(
        export_data,
        json_dumps_params={
            "indent": 4,
            "ensure_ascii": False,
        }
    )

    filename = timezone.now().strftime(
        "soulnote-export-%Y-%m-%d.json"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{filename}"'
    )

    response["Cache-Control"] = "private, no-store"
    response["X-Content-Type-Options"] = "nosniff"

    return response



# Data Import Operations
import json
import logging

logger = logging.getLogger(__name__)

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils.dateparse import parse_datetime
from django.core.exceptions import ValidationError


@login_required(login_url='landing')
@require_http_methods(["GET", "POST"])
def import_data_view(request):

    if request.method == 'POST':

        uploaded_file = request.FILES.get('import_file')

        if not uploaded_file:
            return render(request, 'diary/import-data.html', {
                'error': 'Please select a JSON export file.'
            })

        # Enforce a 10 MB upload limit.
        if uploaded_file.size > 10 * 1024 * 1024:
            return render(request, 'diary/import-data.html', {
                'error': 'The file exceeds the 10 MB upload limit.'
            })

        try:
            raw_data = uploaded_file.read().decode('utf-8-sig')
            data = json.loads(raw_data)

        except (UnicodeDecodeError, json.JSONDecodeError):
            return render(request, 'diary/import-data.html', {
                'error': 'The selected file is not valid UTF-8 JSON.'
            })

        # Validate export structure.
        if not isinstance(data, dict):
            error = 'Invalid SoulNote export structure.'

        elif data.get('format') != 'SoulNote Data Export':
            error = 'This file is not a recognized SoulNote export.'

        elif data.get('schema_version') != '1.0':
            error = 'This export uses an unsupported schema version.'

        elif not isinstance(data.get('diary_entries'), list):
            error = 'The diary entries section is missing or invalid.'

        else:
            error = None

        if error:
            return render(request, 'diary/import-data.html', {
                'error': error
            })

        entries_data = data['diary_entries']

        if len(entries_data) > 5000:
            return render(request, 'diary/import-data.html', {
                'error': 'The export contains more than 5,000 entries.'
            })

        entries_to_create = []

        try:
            for index, item in enumerate(entries_data, start=1):

                if not isinstance(item, dict):
                    raise ValueError(
                        f'Entry {index} has an invalid structure.'
                    )

                content = item.get('content')
                emotions = item.get('detected_emotions')
                reflection = item.get('ai_reflection')
                ip_address = item.get('ip_address')

                if not isinstance(content, str) or not content.strip():
                    raise ValueError(
                        f'Entry {index} has invalid or empty content.'
                    )

                if emotions is not None:
                    if not isinstance(emotions, str) or len(emotions) > 50:
                        raise ValueError(
                            f'Entry {index} has invalid emotion data.'
                        )

                if reflection is not None:
                    if not isinstance(reflection, str):
                        raise ValueError(
                            f'Entry {index} has invalid reflection data.'
                        )

                if ip_address is not None:
                    if not isinstance(ip_address, str):
                        raise ValueError(
                            f'Entry {index} has an invalid IP address.'
                        )

                    DiaryEntry._meta.get_field(
                        'ip_address'
                    ).clean(ip_address, None)

                # Validate timestamps.
                created_at_raw = item.get('created_at')
                updated_at_raw = item.get('updated_at')

                if not isinstance(created_at_raw, str):
                    raise ValueError(
                        f'Entry {index} has an invalid creation timestamp.'
                    )

                if not isinstance(updated_at_raw, str):
                    raise ValueError(
                        f'Entry {index} has an invalid update timestamp.'
                    )

                created_at = parse_datetime(created_at_raw)
                updated_at = parse_datetime(updated_at_raw)

                if not created_at or not updated_at:
                    raise ValueError(
                        f'Entry {index} has invalid timestamps.'
                    )

                # Read UUID or create a deterministic UUID for legacy backups.
                raw_uuid = item.get('entry_uuid')

                if raw_uuid:
                    try:
                        entry_uuid = uuid.UUID(str(raw_uuid))
                    except (ValueError, TypeError, AttributeError):
                        raise ValueError(
                            f'Entry {index} has an invalid UUID.'
                        )

                else:
                    # Legacy backups do not contain UUIDs.
                    # Generate the same UUID for the same legacy entry
                    # whenever that backup is imported again.
                    legacy_identity = json.dumps(
                        [
                            content,
                            emotions,
                            reflection,
                            ip_address,
                            created_at.isoformat(),
                            updated_at.isoformat(),
                        ],
                        ensure_ascii=False,
                        separators=(',', ':')
                    )

                    entry_uuid = uuid.uuid5(
                        uuid.NAMESPACE_URL,
                        'soulnote-legacy-entry:' + legacy_identity
                    )

                entries_to_create.append(
                    DiaryEntry(
                        entry_uuid=entry_uuid,
                        user=request.user,
                        content=content,
                        detected_emotions=emotions,
                        ai_reflection=reflection,
                        ip_address=ip_address,
                        created_at=created_at,
                        updated_at=updated_at,
                    )
                )

        except (
            ValueError,
            TypeError,
            AttributeError,
            ValidationError
        ) as exc:

            return render(request, 'diary/import-data.html', {
                'error': str(exc)
            })

        # Import entries while skipping duplicates.
        imported_count = 0
        skipped_count = 0

        try:
            with transaction.atomic():

                for entry in entries_to_create:

                    exists = DiaryEntry.objects.filter(
                        user=request.user,
                        entry_uuid=entry.entry_uuid
                    ).exists()

                    if exists:
                        skipped_count += 1
                        continue

                    entry.save()

                    # Restore original timestamps.
                    DiaryEntry.objects.filter(
                        pk=entry.pk
                    ).update(
                        created_at=entry.created_at,
                        updated_at=entry.updated_at
                    )

                    imported_count += 1

        except Exception:
            logger.exception("SoulNote data import failed")

            return render(request, 'diary/import-data.html', {
                'error': 'The import failed. Please check the server logs.'
            })

        return render(request, 'diary/import-data.html', {
            'success': True,
            'imported_count': imported_count,
            'skipped_count': skipped_count,
        })

    return render(request, 'diary/import-data.html')


from .models import DiaryEntry

def register_view(request):
	if request.method == 'POST':
		form = RegisterForm(request.POST)

		if form.is_valid():
			user = form.save()
			login(request, user)
			return redirect('home')
	else:
		form = RegisterForm()

	return render(request, 'diary/register.html', {
		'form': form
	})

# Settings View
from django.contrib import messages
from .forms import ProfileUpdateForm


@login_required(login_url='landing')
def settings_view(request):

    if request.method == 'POST':
        form = ProfileUpdateForm(
            request.POST,
            instance=request.user
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Your profile has been updated successfully.'
            )

            return redirect('settings')

    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'diary/settings.html', {
        'profile_form': form,
    })


@login_required(login_url='landing')
def landing_view(request):
	if request.user.is_authenticated:
		return redirect('home')
	return render(request, 'diary/landing.html')

@login_required(login_url='landing')
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
