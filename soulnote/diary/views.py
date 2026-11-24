# Views in Django handle the request and return a response 
# (similar to Flask route functions decorated with @app.route)

import json
import logging
import uuid

from django.http import JsonResponse

from .forms import RegisterForm, DiaryEntryForm
from .forms import ProfileUpdateForm

from .models import DiaryEntry, DiaryEntryRevision

from django.utils import timezone
from django.utils.dateparse import parse_datetime

from django.shortcuts import render, redirect, get_object_or_404

from django.views.decorators.http import require_POST
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_GET

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login

from django.db import transaction
from django.db.models import Max

from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

# Account Delete view

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

# Account data export view

@login_required(login_url='landing')
@require_GET
def export_data_view(request):
	user = request.user

	entries = DiaryEntry.objects.filter(
		user=user
	).prefetch_related('revisions').order_by(
		'created_at', 'id'
	)

	export_data = {
		"format": "SoulNote Data Export",
		"schema_version": "1.1",
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
		
		"revisions": [
			{
				"revision_number": revision.revision_number,
				"content": revision.content,
				"created_at": revision.created_at.isoformat(),
			}
			for entry in entries for revision in entry.revisions.all()
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

# Data Import View
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

		elif data.get('schema_version') not in ('1.0', '1.1'):
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
	
# Register view

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

# Home View

@login_required(login_url='landing')
def home_view(request):
	entries = DiaryEntry.objects.filter(
		user=request.user
	).order_by('-created_at', '-id')

	context = {
		'username': request.user.username,
		'entries': entries,
		'recent_entries': entries[:4],
		'entry_count': entries.count(),
	}

	return render(request, 'diary/home.html', context)

# ---- Diary space ----

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
	
# Diary entry edit

@login_required(login_url='landing')
def edit_entry_view(request, entry_uuid):
    if request.method == 'POST':
        with transaction.atomic():
            entry = get_object_or_404(
                DiaryEntry.objects.select_for_update(),
                entry_uuid=entry_uuid,
                user=request.user
            )

            form = DiaryEntryForm(
                request.POST,
                instance=entry
            )
            if form.is_valid():
                new_content = form.cleaned_data['content']

                preserve_version = (
                    request.POST.get('preserve_version') == 'on'
                )

                content_changed = (
                    new_content != entry.content
                )

                # Preserve the existing version only when explicitly requested.
                if preserve_version and content_changed:

                    DiaryEntryRevision.objects.create(
                        entry=entry,
                        revision_number=get_next_revision_number(entry),
                        content=entry.content
                    )
                # Update the existing entry.
                form.save()

                return redirect(
                    'entry-history',
                    entry_uuid=entry.entry_uuid
                )
    else:
        entry = get_object_or_404(
            DiaryEntry,
            entry_uuid=entry_uuid,
            user=request.user
        )
        form = DiaryEntryForm(instance=entry)

    return render(request, 'diary/edit-entry.html', {
        'form': form,
        'entry': entry,
    })
    
# Delete diary entry

@login_required(login_url='landing')
@require_POST
def delete_entry_view(request, entry_uuid):
    entry = get_object_or_404(
        DiaryEntry,
        entry_uuid=entry_uuid,
        user=request.user
    )

    entry.delete()

    return redirect('home')
    
def get_next_revision_number(entry):
    latest = entry.revisions.aggregate(
        latest_number=Max('revision_number')
    )['latest_number']

    return (latest or 0) + 1
    
# Archhive diary entries views
@login_required(login_url='landing')
def archive_view(request):
    entries = DiaryEntry.objects.filter(
        user=request.user
    ).prefetch_related('revisions').order_by(
        '-created_at', '-id'
    )

    return render(request, 'diary/archive.html', {
        'entries': entries,
        'entry_count': entries.count(),
    })
    
# History views

@login_required(login_url='landing')
def entry_history_view(request, entry_uuid):
    entry = get_object_or_404(
        DiaryEntry.objects.prefetch_related('revisions'),
        entry_uuid=entry_uuid,
        user=request.user
    )
    revisions = list(
        entry.revisions.order_by('revision_number')
    )

    versions = []

    for revision in revisions:
        versions.append({
            'number': revision.revision_number,
            'content': revision.content,
            'saved_at': revision.created_at,
            'is_current': False,
            'revision_id': revision.pk,
        })

    # The current entry is always the last item in the timeline.
    versions.append({
        'number': len(revisions) + 1,
        'content': entry.content,
        'saved_at': entry.updated_at,
        'is_current': True,
        'revision_id': None,
    })

    return render(request, 'diary/entry-history.html', {
        'entry': entry,
        'versions': versions,
        'version_count': len(versions),
    })    
    
# Restore entry
@login_required(login_url='landing')
@require_POST
def restore_entry_revision_view(request, entry_uuid, revision_id):
    with transaction.atomic():
        entry = get_object_or_404(
            DiaryEntry.objects.select_for_update(),
            entry_uuid=entry_uuid,
            user=request.user
        )

        revision = get_object_or_404(
            DiaryEntryRevision,
            pk=revision_id,
            entry=entry
        )

        preserve_current = (
            request.POST.get('preserve_current') == 'on'
        )

        if revision.content != entry.content:

            if preserve_current:
                DiaryEntryRevision.objects.create(
                    entry=entry,
                    revision_number=get_next_revision_number(entry),
                    content=entry.content
                )

            entry.content = revision.content

            entry.save(update_fields=[
                'content',
                'updated_at'
            ])

    return redirect(
        'entry-history',
        entry_uuid=entry.entry_uuid
    )
