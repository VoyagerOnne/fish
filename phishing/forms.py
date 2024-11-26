from django import forms
from .models import *


class PhishingTestForm(forms.ModelForm):
    class Meta:
        model = PhishingTest
        fields = ['name', 'description', 'employees']


class PhishingEmailTemplateForm(forms.ModelForm):
    class Meta:
        model = PhishingEmailTemplate
        fields = ['name', 'subject', 'body', 'interest']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 10, 'cols': 80}),
        }
        labels = {
            'name': 'Название шаблона',
            'subject': 'Тема письма',
            'body': 'Тело письма',
            'interest': 'Тема фишингового сообщения',
        }