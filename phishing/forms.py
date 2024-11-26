from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import *


class EmployeeForm(forms.ModelForm):

    class Meta:
        model = Employee
        fields = ['name', 'email', 'department', 'interests']


class UploadFileForm(forms.Form):
    file = forms.FileField()


class PhishingTestForm(forms.ModelForm):
    employees = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        required=False,
        label="Сотрудники"
    )

    class Meta:
        model = PhishingTest
        fields = ['name', 'description', 'active', 'employees']


class PhishingEmailTemplateForm(forms.ModelForm):
    body = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = PhishingEmailTemplate
        fields = ['name', 'subject', 'body', 'interests']


class FakeLoginForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=255)
    password = forms.CharField(widget=forms.PasswordInput, label="Password")