from django import forms
from contact.models import Contact


class ContactForm(forms.ModelForm):

    enviar_arquivo = forms.ImageField(
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
                  'enviar_arquivo')
