from django import forms
from .models import Category


class CategoryForm(forms.ModelForm):
    name = forms.CharField(required=True)
    parent_id = forms.RegexField(r'\d*', required=False)

    class Meta:
        model = Category
        fields = ('name', 'parent_id',)
