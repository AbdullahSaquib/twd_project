from django import forms
from rango.models import Category, Page, UserProfile
from django.contrib.auth.models import User
from datetime import datetime

class UserForm(forms.ModelForm):
    password = forms.CharField(widget = forms.PasswordInput())
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('website', 'picture')

class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128, help_text = 'Enter New Category Name : ')
    views = forms.IntegerField(widget = forms.HiddenInput(), initial = 0)
    likes = forms.IntegerField(widget = forms.HiddenInput(), initial = 0)
    slug = forms.CharField(widget = forms.HiddenInput(), required = False)

    class Meta:
        model = Category
        fields = ('name',)

class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128, help_text = 'Enter New Page Title : ')
    views = forms.IntegerField(widget = forms.HiddenInput(), initial = 0)
    url = forms.URLField(max_length = 200, help_text = 'Enter URL : ')
    last_visit = forms.DateTimeField(widget = forms.HiddenInput(), initial = datetime.now)

    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')
        if url and not url.startswith('http://'):
            url = 'http://'+url
            cleaned_data['url'] = url
        return cleaned_data

    class Meta:
        model = Page
        exclude = ('category',)
