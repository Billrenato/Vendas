from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cadastrar_produto/', views.cadastrar_produto, name='cadastrar_produto'),
    path('editar_produto/<pk>/', views.editar_produto, name='editar_produto'),
    path('excluir_produto/<pk>/', views.excluir_produto, name='excluir_produto'),

    path('cadastrar_cliente/', views.cadastrar_cliente, name='cadastrar_cliente'),
    path('editar_cliente/<pk>/', views.editar_cliente, name='editar_cliente'),
    path('excluir_cliente/<pk>/', views.excluir_cliente, name='excluir_cliente'),


    path('carrinho/', views.carrinho, name='carrinho'),


     path('resumo-vendas/', views.resumo_vendas, name='resumo_vendas'),
  
    
    

    
]