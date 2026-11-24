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


from .models import Order


class CheckoutForm(forms.Form):
    name = forms.CharField(max_length=200, label="Ismingiz")
    phone = forms.CharField(max_length=20, label="Telefon raqamingiz")
    delivery_type = forms.ChoiceField(
        choices=Order.DeliveryType.choices, label="Qanday olasiz?"
    )
    address = forms.CharField(max_length=300, required=False, label="Manzil")

    def clean(self):
        data = super().clean()
        if data.get("delivery_type") == Order.DeliveryType.DELIVERY and not data.get("address"):
            self.add_error("address", "Yetkazib berish uchun manzilni yozing")
        return data