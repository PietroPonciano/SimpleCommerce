from django.core.mail import EmailMessage
from .models import Produto, Perfil
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class ContatoForm(forms.Form):
    nome = forms.CharField(label='Nome', max_length=100)
    email = forms.CharField(label='E-mail', max_length=100)
    assunto = forms.CharField(label='Assunto', max_length=120)
    mensagem = forms.CharField(label='Mensagem', widget=forms.Textarea())

    def send_mail(self):
        nome = self.cleaned_data['nome']
        email = self.cleaned_data['email']
        assunto = self.cleaned_data['assunto']
        mensagem = self.cleaned_data['mensagem']

        conteudo = f'Nome: {nome}\nEmail: {email}\nAssunto: {assunto}\nMensagem: {mensagem}'

        mail = EmailMessage(
            subject='Email enviado pelo sistema django2',
            body=conteudo,
            from_email='contato@seudominio.com.br',
            to=['contato@seudominio.com.br'],
            headers={'Reply to': email}
        )
        mail.send()

class ProdutoModelForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'preco', 'descricao', 'estoque', 'imagem']

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    telefone = forms.CharField(required=True, max_length=20)

    class Meta:
        model = User
        fields = ['username', 'email', 'telefone','password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit)
        telefone = self.cleaned_data['telefone']
        Perfil.objects.create(user=user, telefone=telefone)
        return user