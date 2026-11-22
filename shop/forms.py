from django import forms
from .models import ContactMessage, Order

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "phone", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "نام و نام خانوادگی"}),
            "phone": forms.TextInput(attrs={"placeholder": "شماره تماس", "inputmode": "tel"}),
            "message": forms.Textarea(attrs={"placeholder": "متن پیام", "rows": 4}),
        }

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["customer_name", "phone", "province_city", "address", "postal_code", "notes"]
        widgets = {
            "customer_name": forms.TextInput(attrs={"placeholder": "نام تحویل‌گیرنده"}),
            "phone": forms.TextInput(attrs={"placeholder": "شماره موبایل", "inputmode": "tel"}),
            "province_city": forms.TextInput(attrs={"placeholder": "استان و شهر"}),
            "address": forms.Textarea(attrs={"placeholder": "نشانی کامل", "rows": 3}),
            "postal_code": forms.TextInput(attrs={"placeholder": "کد پستی"}),
            "notes": forms.Textarea(attrs={"placeholder": "توضیحات اختیاری", "rows": 2}),
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip().replace(" ", "").replace("-", "")
        if len(phone) < 10 or len(phone) > 15:
            raise forms.ValidationError("شماره تماس را بررسی کنید.")
        return phone
