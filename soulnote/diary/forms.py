# diary/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import DiaryEntry

class DiaryEntryForm(forms.ModelForm):
	class Meta:
		model = DiaryEntry
		fields = ['content'] 
		widgets = {
            'content': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Start pouring your thoughts here...',
                'class': 'w-full rounded-xl border border-stone-300 p-4 text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent'
            })
        }

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=100,
        label="Profile Name",
        widget=forms.TextInput(attrs={
            'placeholder': 'What should we call you?'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username',
            'first_name',
            'password1',
            'password2'
        )

        labels = {
            'username': 'Username',
            'first_name': 'Profile Name'
        }
