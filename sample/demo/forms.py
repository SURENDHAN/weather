from django import forms

class state_get(forms.Form):
    name=forms.CharField(max_length=100, required=True)
    
