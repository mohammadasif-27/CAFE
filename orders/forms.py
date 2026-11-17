from django import forms


class DeliveryForm(forms.Form):
    name = forms.CharField(max_length=150)
    phone = forms.RegexField(
        regex=r'^[0-9+\s()-]{7,20}$',
        max_length=30,
    )
    address = forms.CharField(max_length=2000)
    city = forms.CharField(max_length=100)
    pincode = forms.RegexField(regex=r'^\d{6}$', max_length=20)
