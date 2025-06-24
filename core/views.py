from django.shortcuts import render, redirect, get_object_or_404
from .forms import ContatoForm, ProdutoModelForm
from django.contrib import messages
from .models import Produto, Carrinho, ItemCarrinho, ItemPedido, Pedido
from .forms import RegistroForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from .decorators import staff_required_redirect


def index(request):
    carrinho = None
    if request.user.is_authenticated:
        carrinho, _ = Carrinho.objects.get_or_create(usuario=request.user)
    context = {
        'produtos': Produto.objects.all(),
        'carrinho': carrinho,
    }
    return render(request, 'index.html', context)


def acesso_negado(request):
    return render(request, 'acesso_negado.html')


def contato(request):
    form = ContatoForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.send_mail()
            messages.success(request, 'E-mail enviado com sucesso')
            form = ContatoForm()
        else:
            messages.error(request, 'Erro ao enviar e-mail')
    context = {'form': form}
    return render(request, 'contato.html', context)


def produto(request):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
            form = ProdutoModelForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, 'Produto salvo com sucesso.')
                form = ProdutoModelForm()
            else:
                messages.error(request, 'Erro ao salvar produto.')
        else:
            form = ProdutoModelForm()
        return render(request, 'produto.html', {'form': form})
    else:
        return redirect('acesso_negado')


def produto_detalhe(request, id):
    produto = get_object_or_404(Produto, id=id)
    return render(request, 'produto_detalhe.html', {'produto': produto})


def registrar(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = RegistroForm()
    return render(request, 'registro.html', {'form': form})


@login_required
def adicionar_ao_carrinho(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    carrinho, _ = Carrinho.objects.get_or_create(usuario=request.user)
    item, created = ItemCarrinho.objects.get_or_create(carrinho=carrinho, produto=produto)
    if not created:
        item.quantidade += 1
        item.save()
    return redirect('ver_carrinho')


@login_required
def ver_carrinho(request):
    carrinho, _ = Carrinho.objects.get_or_create(usuario=request.user)
    return render(request, 'carrinho.html', {'carrinho': carrinho})


@login_required
def adicionar_quantidade(request, item_id):
    item = get_object_or_404(ItemCarrinho, id=item_id, carrinho__usuario=request.user)
    item.quantidade += 1
    item.save()
    return redirect('ver_carrinho')


@login_required
def remover_quantidade(request, item_id):
    item = get_object_or_404(ItemCarrinho, id=item_id, carrinho__usuario=request.user)
    item.quantidade -= 1
    if item.quantidade <= 0:
        item.delete()
    else:
        item.save()
    return redirect('ver_carrinho')


@login_required
def finalizar_compra(request):
    carrinho = Carrinho.objects.get(usuario=request.user)
    if not carrinho.itens.exists():
        return redirect('index')

    perfil = getattr(request.user, 'perfil', None)
    telefone = 'N/a'
    if perfil and perfil.telefone:
        telefone = perfil.telefone

    email = request.user.email
    pedido = Pedido.objects.create(usuario=request.user, total=carrinho.total(), telefone=telefone, email=email)

    for item in carrinho.itens.all():
        ItemPedido.objects.create(
            pedido=pedido,
            produto=item.produto,
            quantidade=item.quantidade,
            preco_unitario=item.produto.preco
        )

    carrinho.itens.all().delete()

    if request.user.is_staff:
        pedidos = Pedido.objects.filter(usuario=request.user).order_by('-criado')
        return render(request, 'pedidos.html', {'pedidos': pedidos})
    else:
        return redirect('index')


@staff_required_redirect
def listar_usuarios(request):
    User = get_user_model()
    usuarios = User.objects.all()
    return render(request, 'usuarios.html', {'usuarios': usuarios})


@require_POST
@staff_required_redirect
def alterar_staff(request, user_id):
    User = get_user_model()
    usuario = get_object_or_404(User, id=user_id)
    if request.user.is_superuser:
        novo_status = not usuario.is_staff
        usuario.is_staff = novo_status
        usuario.save()
        return redirect('listar_usuarios')
    else:
        return redirect('listar_usuarios')


@staff_required_redirect
def listar_pedidos(request):
    pedidos = Pedido.objects.all()
    return render(request, 'pedidos.html', {'pedidos': pedidos})


@login_required
def deletar_pedido(request, pedido_id):
    if request.user.is_staff:
        pedido = get_object_or_404(Pedido, id=pedido_id)
    else:
        pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    pedido.delete()
    return redirect('listar_pedidos')


@login_required
def meus_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-criado')
    return render(request, 'meus_pedidos.html', {'pedidos': pedidos})


@require_POST
@staff_required_redirect
def atualizar_status(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    novo_status = request.POST.get('status')
    if novo_status in dict(Pedido.STATUS_CHOICES):
        pedido.status = novo_status
        pedido.save()
        messages.success(request, f'Status do pedido #{pedido.id} atualizado para "{pedido.get_status_display()}".')
    return redirect('listar_pedidos')



@login_required
def meu_perfil(request):
    usuario = request.user
    return render(request, 'meu_perfil.html', {'usuario': usuario})

@login_required
def atendimento_ia(request):
    resposta = None

    if request.method == 'POST':
        pergunta = request.POST.get('pergunta', '').lower()

        # Respostas predefinidas com base em palavras-chave
        if "horário" in pergunta or "funciona" in pergunta:
            resposta = "Nosso site funciona 24 horas por dia, 7 dias por semana!"
        elif "contato" in pergunta or "telefone" in pergunta:
            resposta = "Você pode entrar em contato conosco pelo e-mail contato@exemplo.com."
        elif "serviço" in pergunta or "oferece" in pergunta:
            resposta = "Oferecemos serviços de atendimento online, suporte técnico e muito mais."
        elif "ajuda" in pergunta:
            resposta = "Claro! Em que posso te ajudar? Pergunte sobre horário, contato ou serviços."
        else:
            resposta = "Desculpe, não entendi sua pergunta. Tente reformular ou entre em contato conosco."

    return render(request, 'chatbot.html', {'resposta': resposta})