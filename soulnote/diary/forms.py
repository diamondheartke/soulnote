# diary/forms.py

from django import forms
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
