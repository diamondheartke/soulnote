# ava/forms.py

from django import forms

class ChatEntryForm(forms.Form):
	user_input = forms.CharField(
		max_length = 8000,
		label = 'You',
		widget = forms.Textarea(attrs={
			"placeholder": "Pour your thoughts, she's listening"
		})
	)
