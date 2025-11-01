from django import forms
from django.contrib.auth.forms import UserCreationForm
from contact.models import Contact
from contact.models import Entradas


class ContactForm(forms.ModelForm):

    picture = forms.ImageField(
        widget=forms.FileInput(
            attrs={
                'accept': 'img/*',
            }
        ),
        required=False
    )

    class Meta:
        model = Contact
        fields = ('marca', 'descricao_do_produto',
                  'categoria', 'preco_de_catalogo', 'data_de_validade', 'anotacoes','picture')


class RegisterForm(UserCreationForm):
    ...

class EntradasForm(forms.ModelForm):

    class Meta:
        model = Entradas
        fields = ('data_de_entrada', 'descricao_do_produto',
                  'qtd', 'preco_de_custo', 'data_de_validade')