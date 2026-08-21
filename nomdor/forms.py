from django import forms
from nomdor.models import About,Product


class AboutForm(forms.ModelForm):
    class Meta:
        model = About
        fields='__all__'



class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category',
            'name',
            'description',
            'price',
            'image',
            'is_available',
        ]