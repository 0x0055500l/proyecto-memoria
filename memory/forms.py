from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class CustomLoginForm(AuthenticationForm):
    # Traducimos y añadimos la clase 'form-control' para que Bootstrap la tome
    username = forms.CharField(label="Nombre de usuario", 
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu usuario'}))
    password = forms.CharField(label="Contraseña", 
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Tu contraseña'}))

class CustomRegisterForm(UserCreationForm):
    # El PDF pedía un email, así que lo añadimos
    email = forms.EmailField(label="Correo electrónico", 
                             required=True,
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'tu@correo.com'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email') # Dejamos solo username y email
        labels = {
            'username': 'Nombre de usuario',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añadimos 'form-control' a todos los campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'username':
                field.widget.attrs['placeholder'] = 'Crea tu nombre de usuario'

    def clean_email(self):
        # Validación extra: Asegura que el email sea único
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está en uso.")
        return email