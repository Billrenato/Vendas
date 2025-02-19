from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Produto, Cliente, Venda, Carrinho
from .forms import ProdutoForm, ClienteForm, VendaForm
from django.template.loader import get_template
import uuid
from decimal import Decimal
from django.db.models import Q

def home(request):
    return render(request, 'vendas/home.html', {})



def cadastrar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
    form = ProdutoForm()
    produtos = Produto.objects.all()
    q = request.GET.get('q', '')
    if q:
        produtos = Produto.objects.filter(descricao__icontains=q)
    return render(request, 'vendas/cadastrar_produto.html', {'form': form, 'produtos': produtos})





def editar_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto editado com sucesso!')
            return redirect('cadastrar_produto')
    else:
        form = ProdutoForm(instance=produto)
    return render(request, 'vendas/editar_produto.html', {'form': form})



def excluir_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        produto.delete()
        messages.success(request, 'Produto Excluido!')
        return redirect('cadastrar_produto')
    return render(request, 'vendas/editar_produto.html', {'produto': produto})

#----------------------------------------------------------------------------------------------------------#

def cadastrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
    form = ClienteForm()
    clientes = Cliente.objects.all()
    q = request.GET.get('q', '')
    if q:
        clientes = Cliente.objects.filter(nome__icontains=q)
    return render(request, 'vendas/cadastrar_cliente.html', {'form': form, 'clientes': clientes})


def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente editado com sucesso!')
            return redirect('cadastrar_cliente')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'vendas/editar_cliente.html', {'form': form})


def excluir_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente Excluido!')
        return redirect('cadastrar_cliente')
    return render(request, 'vendas/editar_cliente.html', {'cliente': cliente})

#------------------------------------------------------------------------------------------------------------------------------#
def gerar_id_venda():
    return uuid.uuid4().hex


def carrinho(request):
    carrinho = Carrinho.objects.all()
    produtos = Produto.objects.all()
    clientes = Cliente.objects.all()
    resultados_cliente = None
    resultados_produto = None
    mensagem_cliente = None
    mensagem_produto = None

    if request.method == 'POST':
        if 'buscar_cliente' in request.POST:
            nome_cliente = request.POST.get('nome_cliente')
            resultados_cliente = Cliente.objects.filter(nome__icontains=nome_cliente)
            if not resultados_cliente:
                mensagem_cliente = "Cliente não encontrado"
            return render(request, 'vendas/carrinho.html', {'resultados_cliente': resultados_cliente, 'mensagem_cliente': mensagem_cliente, 'carrinho': carrinho, 'produtos': produtos, 'clientes': clientes})

        elif 'selecionar_cliente' in request.POST:
            cliente_selecionado = request.POST.get('cliente_selecionado')
            cliente = Cliente.objects.get(pk=cliente_selecionado)
            if not Carrinho.objects.filter(cliente__isnull=False).exists():
                Carrinho.objects.create(cliente=cliente)
                mensagem = "Cliente adicionado ao carrinho com sucesso!"
            else:
                mensagem = "Já existe um cliente adicionado ao carrinho."
            return render(request, 'vendas/carrinho.html', {'mensagem': mensagem, 'carrinho': carrinho, 'produtos': produtos, 'clientes': clientes})

        elif 'buscar_produto' in request.POST:
            descricao_produto = request.POST.get('descricao_produto')
            resultados_produto = Produto.objects.filter(descricao__icontains=descricao_produto)
            if not resultados_produto:
                mensagem_produto = "Produto não encontrado"
            return render(request, 'vendas/carrinho.html', {'resultados_produto': resultados_produto, 'mensagem_produto': mensagem_produto, 'carrinho': carrinho, 'produtos': produtos, 'clientes': clientes})

        elif 'selecionar_produto' in request.POST:
            produto_selecionado = request.POST.get('produto_selecionado')
            produto = Produto.objects.get(pk=produto_selecionado)
            quantidade = request.POST.get('quantidade')
            total = produto.preco * int(quantidade)
            Carrinho.objects.create(produto=produto, quantidade=int(quantidade), total=total)
            return redirect('carrinho')

        elif 'remover_produto' in request.POST:
            carrinho = Carrinho.objects.get(pk=request.POST.get('carrinho'))
            carrinho.delete()
            return redirect('carrinho')

        elif 'aplicar_desconto' in request.POST:
            desconto_porcentagem = request.POST.get('desconto_porcentagem')
            carrinho = Carrinho.objects.all()
            for item in carrinho:
                if item.total is not None:
                    desconto = (item.total * Decimal(desconto_porcentagem)) / 100
                    item.total -= desconto
                    item.save()
                else:
                    item.total = 0
                    desconto = (item.total * Decimal(desconto_porcentagem)) / 100
                    item.total -= desconto
                    item.save()
            return redirect('carrinho')

        elif 'finalizar_compra' in request.POST:
            desconto_porcentagem = request.POST.get('desconto_porcentagem', None)
            desconto = request.POST.get('desconto', None)
            if desconto is None or desconto == "":
                desconto = 0
            carrinho = Carrinho.objects.all()
            for item in carrinho:
                if item.produto is not None:
                    if item.quantidade is not None:
                        Venda.objects.create(
                            produto=item.produto,
                            cliente=carrinho[0].cliente,
                            quantidade=item.quantidade,
                            total=item.total,
                            desconto=desconto,
                            id_venda=gerar_id_venda()
                        )
                    else:
                        item.delete()
                else:
                    continue
            carrinho.delete()
            mensagem = "Venda finalizada com sucesso!"
            id_venda = gerar_id_venda()
            return render(request, 'vendas/carrinho.html', {'mensagem': mensagem, 'id_venda': id_venda, 'carrinho': carrinho, 'produtos': produtos, 'clientes': clientes})

    total = 0
    for item in carrinho:
        if item.total is not None:
            total += item.total

    return render(request, 'vendas/carrinho.html', {'carrinho': carrinho, 'produtos': produtos, 'clientes': clientes, 'total': total, 'resultados_cliente': resultados_cliente, 'resultados_produto': resultados_produto, 'mensagem_cliente': mensagem_cliente, 'mensagem_produto': mensagem_produto})

#-------------------------------------------------------------------------------------#



def resumo_vendas(request):
    vendas = Venda.objects.all()
    pesquisa = request.GET.get('pesquisa')
    data_inicial = request.GET.get('data_inicial')
    data_final = request.GET.get('data_final')

    if pesquisa:
        vendas = vendas.filter(Q(cliente__nome__icontains=pesquisa))

    if data_inicial and data_final:
        vendas = vendas.filter(data_venda__range=[data_inicial, data_final])

    return render(request, 'vendas/resumo_vendas.html', {'vendas': vendas})
