from django.urls import path
from . import views 
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='vendas/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),
    

    path('cadastrar_empresa/', views.cadastrar_empresa, name='cadastrar_empresa'),
    path('editar_empresa/<pk>/', views.editar_empresa, name='editar_empresa'), 


    path('cadastrar_produto/', views.cadastrar_produto, name='cadastrar_produto'),
    path('editar_produto/<pk>/', views.editar_produto, name='editar_produto'),
    path('excluir_produto/<pk>/', views.excluir_produto, name='excluir_produto'),
    path('excluir-imagem-produto/<int:imagem_id>/', views.excluir_imagem_produto, name='excluir_imagem_produto'),
    
    

    path('cadastrar_cliente/', views.cadastrar_cliente, name='cadastrar_cliente'),
    path('editar_cliente/<pk>/', views.editar_cliente, name='editar_cliente'),
    path('excluir_cliente/<pk>/', views.excluir_cliente, name='excluir_cliente'),

    path('cadastrar_vendedor/', views.cadastrar_vendedor, name='cadastrar_vendedor'),
    path('editar_vendedor/<pk>/', views.editar_vendedor, name='editar_vendedor'),
    path('excluir_vendedor/<pk>/', views.excluir_vendedor, name='excluir_vendedor'),

    
    path("cadastrar_venda/",  views.cadastrar_venda, name="cadastrar_venda"),
    
    path("finalizar_venda/<int:venda_id>/",  views.finalizar_venda, name="finalizar_venda"),

    path('nfce/visualizar/<int:venda_id>/', views.visualizar_nfce, name='visualizar_nfce'),
    path('nfce/emitir/<int:venda_id>/', views.emitir_nfce, name='emitir_nfce'),
    path("gerar_pdf/<int:venda_id>/",  views.gerar_pdf_venda, name="gerar_pdf_venda"),
    path("pesquisar_venda/", views.pesquisar_venda, name="pesquisar_venda"),
    path("editar_venda/<int:venda_id>/", views.editar_venda, name="editar_venda"),
    path("limpar_campos/<int:venda_id>/", views.limpar_campos_venda, name="limpar_campos_venda"),

    path('resumo-vendas/', views.resumo_vendas, name='resumo_vendas'),

    path('nfe/', views.gerar_nfe, name='gerar_nfe'),
    path('nfe/enviar/<pk>/', views.enviar_xml, name='enviar_xml'),
    path('nfe/enviado/', views.nfe_enviado, name='nfe_enviado'),


    
    path('despesas/', views.despesas, name='despesas'),
    

    path('vendas/conta-cliente/', views.vendas_conta_cliente, name='vendas_conta_cliente'),
   
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)