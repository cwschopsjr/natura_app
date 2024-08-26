from django import forms
from contact.models import Contact
from django.shortcuts import render
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import password_validation


class ContactForm(forms.ModelForm):

    enviar_arquivo = forms.ImageField(
        widget=forms.FileInput(
            attrs={
                'accept': 'img/*',
            }
        ),
        required=False
    )
    # data_da_consulta = forms.DateField(
    #     widget=forms.DateInput(
    #         attrs={
    #             'placeholder': 'dd/mm/aaaa',
    #         }
    #     ),
    #     required=False
    # )

    class Meta:
        model = Contact
        fields = ('marca', 'descricao_do_produto',
                  'categoria', 'qtd', 'preco', 'anotacoes',
                  'enviar_arquivo')

    # def clean(self):
    #     cleaned_data = self.cleaned_data
    #     nome_do_paciente = cleaned_data.get('nome_do_paciente')
    #     hd = cleaned_data.get('hd')
    #     if nome_do_paciente == hd:
    #         msg = ValidationError(
    #             'O nome está igual ao hd',
    #             code='invalid'
    #         )
    #         self.add_error('nome_do_paciente', msg)
    #     return super().clean()


class RegisterForm(UserCreationForm):
    primeiro_nome = forms.CharField(
        required=True,
        min_length=3,
    )
    sobrenome = forms.CharField(
        required=True,
        min_length=3,
    )
    email = forms.EmailField()

    class Meta:
        model = User
        fields = (
            'primeiro_nome', 'sobrenome', 'email',
            'username', 'password1', 'password2',
        )

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            self.add_error(
                'email',
                ValidationError('Já existe este e-mail', code='invalid')
            )

        return email


class RegisterUpdateForm(forms.ModelForm):
    primeiro_nome = forms.CharField(
        min_length=2,
        max_length=30,
        required=True,
        help_text='Required.',
        error_messages={
            'min_length': 'Por favor, adicione mais que 2 letras'
        }
    )
    sobrenome = forms.CharField(
        min_length=2,
        max_length=30,
        required=True,
        help_text='Required.'
    )

    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html(),
        required=False,
    )

    password2 = forms.CharField(
        label="Password 2",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text='Use the same password as before.',
        required=False,
    )

    class Meta:
        model = User
        fields = (
            'primeiro_nome', 'sobrenome', 'email',
            'username',
        )

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        user = super().save(commit=False)
        password = cleaned_data.get('password1')

        if password:
            user.set_password(password)

        if commit:
            user.save()

        return user

    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 or password2:
            if password1 != password2:
                self.add_error(
                    'password2',
                    ValidationError('Senhas não batem')
                )

        return super().clean()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        current_email = self.instance.email

        if current_email != email:
            if User.objects.filter(email=email).exists():
                self.add_error(
                    'email',
                    ValidationError('Já existe este e-mail', code='invalid')
                )

        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')

        if password1:
            try:
                password_validation.validate_password(password1)
            except ValidationError as errors:
                self.add_error(
                    'password1',
                    ValidationError(errors)
                )

        return password1
