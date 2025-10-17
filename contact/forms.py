from django import forms
from django.contrib.auth.forms import UserCreationForm
from contact.models import Contact


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
                  'categoria', 'qtd', 'preco', 'anotacoes',
                  'picture')


class RegisterForm(UserCreationForm):
    ...
