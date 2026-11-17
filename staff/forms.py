from django import forms
from menu.models import Food


class FoodForm(forms.ModelForm):
    class Meta:
        model = Food
        fields = ["name", "description", "category", "price", "available", "image"]

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("Enter a food name.")
        return name

    def clean_category(self):
        category = self.cleaned_data["category"].strip()
        if not category:
            raise forms.ValidationError("Enter a category.")
        return category