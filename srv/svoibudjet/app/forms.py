from django import forms
from .models import Category


class CategoryForm(forms.ModelForm):
    name = forms.CharField(required=True)
    parent = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)

    class Meta:
        model = Category
        fields = ('name', 'parent',)
