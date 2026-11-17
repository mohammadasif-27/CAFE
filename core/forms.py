from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(max_length=150)
    email = forms.EmailField(max_length=254)
    phone = forms.RegexField(
        regex=r'^[0-9+\s()-]{7,20}$',
        max_length=20,
    )
    message = forms.CharField(max_length=2000, strip=True)


class ReviewForm(forms.Form):
    rating = forms.ChoiceField(choices=[(value, str(value)) for value in range(1, 6)])
    message = forms.CharField(max_length=2000, strip=True)
