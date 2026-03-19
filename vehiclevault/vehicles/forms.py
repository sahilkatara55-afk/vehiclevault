from django import forms
from .models import Car, FavoriteVehicle, CompareHistory, UserDocument, Reminder, Accessory, AdminNotification

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['make', 'model', 'year', 'min_price', 'max_price', 'mileage', 'engine', 'transmission', 'safety_rating', 'image', 'description']
        widgets = {
            'make': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Make'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Model'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2024'}),
            'min_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Min Price'}),
            'max_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Max Price'}),
            'mileage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 20 kmpl'}),
            'engine': forms.Select(attrs={'class': 'form-select'}),
            'transmission': forms.Select(attrs={'class': 'form-select'}),
            'safety_rating': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Car Description'}),
        }

class UserDocumentForm(forms.ModelForm):
    class Meta:
        model = UserDocument
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Document Title (e.g., License, Insurance)'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }

class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        fields = ['title', 'type', 'due_date', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reminder Title'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any additional notes...'}),
        }

class AccessoryForm(forms.ModelForm):
    class Meta:
        model = Accessory
        fields = ['name', 'compatible_car', 'price', 'image', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Accessory Name'}),
            'compatible_car': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Compatible Cars (e.g., Universal, Honda City)'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Accessory description...'}),
        }

class AdminNotificationForm(forms.ModelForm):
    class Meta:
        model = AdminNotification
        fields = ['title', 'message', 'sent_to_all', 'recipients']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Notification Title'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Type your message here...'}),
            'sent_to_all': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'margin-left: 10px;'}),
            'recipients': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }