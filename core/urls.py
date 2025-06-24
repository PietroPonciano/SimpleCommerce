# core/urls.py

from django.urls import path
from .views import index, contato, produto
from core import views
from django.contrib import admin
from django.urls import path, include
from core import views

from django.conf.urls.static import static
from django.conf import settings

from django.contrib.auth import views as auth_views
from django.urls import path
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', index, name='index'),
    path('contato/', contato, name='contato'),
    path('produto/', produto, name='produto'),
    path('registro/', views.registrar, name='registro'),
    path('produto/<int:id>/', views.produto_detalhe, name='produto_detalhe'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('adicionar-ao-carrinho/<int:produto_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('carrinho/', views.ver_carrinho, name='ver_carrinho'),
    path('carrinho/adicionar/<int:item_id>/', views.adicionar_quantidade, name='adicionar_quantidade'),
    path('carrinho/remover/<int:item_id>/', views.remover_quantidade, name='remover_quantidade'),
    path('finalizar-compra/', views.finalizar_compra, name='finalizar_compra'),
    path('pedidos/', views.listar_pedidos, name='listar_pedidos'),
    path('pedido/<int:pedido_id>/deletar/', views.deletar_pedido, name='deletar_pedido'),
    path('meus_pedidos/', views.meus_pedidos, name='meus_pedidos'),
    path('pedido/<int:pedido_id>/status/', views.atualizar_status, name='atualizar_status'),
    path('usuarios/', views.listar_usuarios, name='listar_usuarios'),
    path('usuarios/alterar-staff/<int:user_id>/', views.alterar_staff, name='alterar_staff'),
    path('acesso-negado/', views.acesso_negado, name='acesso_negado'),
    path('meu_perfil/', views.meu_perfil, name='meu_perfil'),
    path('chat/', views.atendimento_ia, name='chat_ia'),


]
