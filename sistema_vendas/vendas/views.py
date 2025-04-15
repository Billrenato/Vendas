from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Produto, Cliente, Venda, Vendedor, Empresa, Despesa
from .forms import ProdutoForm, ClienteForm, VendedorForm, EmpresaForm, DespesaForm
from django.template.loader import get_template
import uuid
from decimal import Decimal
from django.db.models import Q
from .forms import NFeForm
from .models import NFe
from OpenSSL import crypto
from xml.etree.ElementTree import Element, tostring
from django.shortcuts import render
from django.http import HttpResponse
import pdfkit
from datetime import datetime
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from urllib.parse import quote_plus
import plotly.graph_objects as go
import pandas as pd
import json
from django.shortcuts import render
from .models import Venda, Vendedor
import plotly.utils
import plotly.express as px


@login_required
def home(request):
    vendas = Venda.objects.all()
    df_vendas = pd.DataFrame(list(vendas.values('vendedor_id', 'total', 'data_venda')))

    if not df_vendas.empty:
        df_vendas['data_venda'] = pd.to_datetime(df_vendas['data_venda'])

        # Gráfico de barras do resumo de vendas dos últimos 6 meses
        df_vendas_meses = df_vendas.groupby(pd.Grouper(key='data_venda', freq='ME')).sum()
        fig1 = go.Figure(data=[go.Scatter(x=df_vendas_meses.index.strftime('%Y-%m-%d'), y=df_vendas_meses['total'], mode='lines')])
        fig1.update_layout(
        title='Resumo de Vendas dos Últimos 6 Meses',
        height=400,  # altura do gráfico
        autosize=True,  # ajusta automaticamente o tamanho do gráfico
            xaxis=dict(
            tickformat='%Y-%m-%d',  # formato da data no eixo x
            tickangle=-45  # ângulo da data no eixo x
            )
        )
        

        # Indicador com o valor bruto de vendas do mês atual
        df_vendas_mes_atual = df_vendas[df_vendas['data_venda'].dt.month == pd.Timestamp.now().month]
        valor_bruto_mes_atual = df_vendas_mes_atual['total'].sum()
        fig2 = go.Figure(data=[go.Indicator(mode="number",value=valor_bruto_mes_atual,title={'text': "Vendas do Mês Atual", 'font': {'size': 12}},number={'prefix': "R$", 'valueformat': ",.2f"})])
        fig2.update_layout(
        height=220,  # altura do gráfico
        font=dict(size=16)  # tamanho da fonte
        )


        # Rank de vendas por vendedores
        df_vendas_vendedores = df_vendas.groupby('vendedor_id')['total'].sum().reset_index()
        df_vendedores = pd.DataFrame(list(Vendedor.objects.all().values('id', 'nome_vendedor')))
        df_vendas_vendedores = df_vendas_vendedores.merge(df_vendedores, left_on='vendedor_id', right_on='id')
        df_vendas_vendedores = df_vendas_vendedores.drop(['vendedor_id', 'id'], axis=1)
        df_vendas_vendedores = df_vendas_vendedores.rename(columns={'nome_vendedor': 'vendedor'})
        df_vendas_vendedores = df_vendas_vendedores.sort_values(by='total', ascending=False).head(10)
        fig3 = go.Figure(data=[go.Bar(x=df_vendas_vendedores['vendedor'],y=df_vendas_vendedores['total'],marker=dict(color=[px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)] for i in range(len(df_vendas_vendedores))]))])
        fig3.update_layout(title='Rank de Vendas por Vendedores')
       
        df_vendas_dia_atual = df_vendas[df_vendas['data_venda'].dt.date == pd.Timestamp.now().date()]
        valor_bruto_dia_atual = df_vendas_dia_atual['total'].sum()
        fig4 = go.Figure(data=[go.Indicator(mode="number",value=valor_bruto_dia_atual,title={'text': "Vendas do Dia Atual", 'font': {'size': 12}},number={'prefix': "R$", 'valueformat': ",.2f"})])
        fig4.update_layout(
        height=220,  # altura do gráfico
        font=dict(size=16)  # tamanho da fonte
        )
        

        # Vendas do ano atual
        df_vendas_ano_atual = df_vendas[df_vendas['data_venda'].dt.year == pd.Timestamp.now().year]
        valor_bruto_ano_atual = df_vendas_ano_atual['total'].sum()
        fig5 = go.Figure(data=[go.Indicator(mode="number",value=valor_bruto_ano_atual,title={'text': "Vendas do Ano Atual", 'font': {'size': 12}},number={'prefix': "R$", 'valueformat': ",.2f"})])
        fig5.update_layout(
        height=220,  # altura do gráfico
        font=dict(size=16)  # tamanho da fonte
        )


        # Calcula a participação de cada produto nas vendas totais
        itens_venda = ItemVenda.objects.all()
        df_itens_venda = pd.DataFrame(list(itens_venda.values('produto_id', 'quantidade', 'preco_unitario', 'subtotal')))
        df_produtos = pd.DataFrame(list(Produto.objects.all().values('id', 'descricao')))
        df_itens_venda = df_itens_venda.merge(df_produtos, left_on='produto_id', right_on='id')
        df_itens_venda = df_itens_venda.drop(['produto_id', 'id'], axis=1)
        df_itens_venda = df_itens_venda.rename(columns={'descricao': 'produto'})

# Calcula a participação de cada produto nas vendas totais
        df_itens_venda['participacao'] = df_itens_venda['subtotal'] / df_itens_venda['subtotal'].sum()
        df_itens_venda = df_itens_venda.sort_values(by='participacao', ascending=False)
        df_itens_venda['acumulado'] = df_itens_venda['participacao'].cumsum()

# Plota a curva ABC
        fig6 = go.Figure(data=[go.Scatter(x=df_itens_venda.index, y=df_itens_venda['acumulado'], mode='lines')])
        fig6.update_layout(
            title='Curva ABC de Produtos',
            xaxis_title='Produtos',
            yaxis_title='Participação Acumulada'
        )


        
        # Calcula os produtos mais vendidos
        df_produtos_mais_vendidos = df_itens_venda.groupby('produto')['subtotal'].sum().reset_index()
        df_produtos_mais_vendidos = df_produtos_mais_vendidos.sort_values(by='subtotal', ascending=False).head(10)

        # Plota o gráfico de pizza
        fig7 = go.Figure(data=[go.Pie(labels=df_produtos_mais_vendidos['produto'], values=df_produtos_mais_vendidos['subtotal'])])
        fig7.update_layout(title='Produtos Mais Vendidos')



        





# Desabilitar o ModeBar

        


        # Converter gráficos para JSON
        graph_json1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
        graph_json2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
        graph_json3 = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
        graph_json4 = json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)
        graph_json5 = json.dumps(fig5, cls=plotly.utils.PlotlyJSONEncoder)
        graph_json6 = json.dumps(fig6, cls=plotly.utils.PlotlyJSONEncoder)
        graph_json7 = json.dumps(fig7, cls=plotly.utils.PlotlyJSONEncoder)

        context = {
            'graph_json1': graph_json1,
            'graph_json2': graph_json2,
            'graph_json3': graph_json3,
            'graph_json4': graph_json4,
            'graph_json5': graph_json5,
            'graph_json6': graph_json6,
            'graph_json7': graph_json7,
        }
        return render(request, 'vendas\home.html', context)
    else:
        # Se o banco de dados estiver vazio, renderize a página com uma mensagem
        return render(request, 'vendas\home.html', {'mensagem': 'O banco de dados está vazio.'})

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redireciona para a página inicial após o cadastro
    else:
        form = UserCreationForm()
    
    return render(request, 'vendas/register.html', {'form': form}) 

#--------------------------------------------Dados da empresa------------------------------------------#
def cadastrar_empresa(request):
    empresa = Empresa.objects.first()
    if empresa:
        return redirect('editar_empresa', pk=empresa.pk)
    if request.method == 'POST':
        form = EmpresaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cadastrar_empresa')
    else:
        form = EmpresaForm()
    return render(request, 'vendas/cadastrar_empresa.html', {'form': form})


def editar_empresa(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    if request.method == 'POST':
        form = EmpresaForm(request.POST, instance=empresa)
        if form.is_valid():
            form.save()
            return redirect('cadastrar_empresa')
    else:
        form = EmpresaForm(instance=empresa)
    return render(request, 'vendas/cadastrar_empresa.html', {'form': form, 'empresa': empresa})



#---------------------------------------------CADASTRO DE PRODUTOS-------------------------------------------------#
import requests
import json
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ProdutoFormComImagens
from .models import Produto, ImagemProduto
import urllib.parse
from django.conf import settings


MERCADO_LIVRE_ACCESS_TOKEN = settings.MERCADO_LIVRE_ACCESS_TOKEN  # Agora está globalizado

MERCADO_LIVRE_API_URL = "https://api.mercadolibre.com"

def obter_categoria(descricao):
    """Busca a melhor categoria para um produto com base na descrição."""
    url = f"{MERCADO_LIVRE_API_URL}/sites/MLB/domain_discovery/search?q={descricao}"
    headers = {"Authorization": f"Bearer {MERCADO_LIVRE_ACCESS_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        categorias = response.json()
        if categorias:
            return categorias[0]["category_id"]
    return None

def obter_atributos_obrigatorios(category_id):
    """Obtém os atributos obrigatórios para uma categoria no Mercado Livre."""
    url = f"{MERCADO_LIVRE_API_URL}/categories/{category_id}/attributes"
    headers = {"Authorization": f"Bearer {MERCADO_LIVRE_ACCESS_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        atributos = response.json()
        return [attr for attr in atributos if "required" in attr.get("tags", [])]
    return []

def publicar_no_mercado_livre(produto_id):
    """Publica o produto no Mercado Livre."""
    try:
        produto = Produto.objects.get(id=produto_id)

        # 1️⃣ Buscar a categoria do produto
        category_id = obter_categoria(produto.descricao)
        if not category_id:
            return {"erro": "Categoria não encontrada"}

        # 2️⃣ Obter atributos obrigatórios da categoria
        atributos_obrigatorios = obter_atributos_obrigatorios(category_id)

        # 3️⃣ Montar os atributos com base no banco de dados
        atributos = []
        for atributo in atributos_obrigatorios:
            if atributo["id"] == "BRAND":
                atributos.append({"id": "BRAND", "value_name": produto.marca})
            elif atributo["id"] == "MODEL":
                atributos.append({"id": "MODEL", "value_name": produto.descricao})
            elif atributo["id"] == "COLOR" and produto.prod_cor:
                atributos.append({"id": "COLOR", "value_name": produto.prod_cor})
            elif atributo["id"] == "MATERIAL":
                atributos.append({"id": "MATERIAL", "value_name": produto.material})
            elif atributo["id"] == "OBJECT_TYPE":
                atributos.append({"id": "OBJECT_TYPE", "value_name": produto.object_type})   
            # Verifique se o atributo GTIN está entre os obrigatórios
        if any(attr["id"] == "GTIN" for attr in atributos_obrigatorios):
            if produto.codigo_barras:
                atributos.append({"id": "GTIN", "value_name": produto.codigo_barras})
            else:
                print("GTIN não encontrado para o produto.")
                return {"erro": "GTIN é obrigatório para esta categoria, mas o código de barras está ausente"}
        

        imagens = produto.imagens.all()
        if imagens:
            pictures = [{"source": imagem.imagem.url} for imagem in imagens]
        else:
            pictures = []

        if produto.codigo_barras:
           atributos.append({"id": "GTIN", "value_name": produto.codigo_barras})



        # 4️⃣ Montar os dados do produto
        dados_produto = {
            "title": produto.descricao,
            "category_id": category_id,
            "price": float(produto.preco),  
            "currency_id": "BRL",
            "available_quantity": produto.quantidade,
            "buying_mode": "buy_it_now",
            "listing_type_id": "gold_special",
            "condition": "new" if produto.condicao == "novo" else "used" if produto.condicao == "usado" else "not_specified",
            "pictures": pictures,
            "attributes": atributos,
            "shipping": {
                "mode": "me2" if produto.tipo_envio == "mercado_envios" else "custom",
                "local_pick_up": True if produto.tipo_envio == "retirada" else False,
                "free_shipping": produto.envio_gratis,
                "dimensions": f"{int(produto.altura*100)}x{int(produto.largura*100)}x{int(produto.profundidade*100)},{int(produto.peso*100)}",
                 }
            }
        
    
    

        # Print do JSON enviado para o Mercado Livre
        print("JSON gerado para envio ao Mercado Livre:")
        print(json.dumps(dados_produto, indent=4))

        # 5️⃣ Enviar para o Mercado Livre
        url = f"{MERCADO_LIVRE_API_URL}/items"
        headers = {
            "Authorization": f"Bearer {MERCADO_LIVRE_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, data=json.dumps(dados_produto))

        # 6️⃣ Verificar resposta
        if response.status_code == 201:
            resposta_ml = response.json()
            produto.mercado_livre_id = resposta_ml["id"]
            produto.link_mercado_livre = resposta_ml["permalink"]
            produto.save()
            return resposta_ml
        else:
            resposta_ml = response.json()
            erro_msg = resposta_ml.get('message', 'Erro desconhecido')
            detalhes_erro = resposta_ml.get('cause', [])
            print("Erro ao publicar produto no Mercado Livre:")
            print(f"Mensagem de erro: {erro_msg}")
            print(f"Detalhes do erro: {detalhes_erro}")
            return {"erro": f"Validation error: {erro_msg}"}

    except Produto.DoesNotExist:
        print("Erro: Produto não encontrado")
        return {"erro": "Produto não encontrado"}
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return {"erro": f"Erro inesperado: {str(e)}"}


def excluir_do_mercado_livre(ml_product_id):
    """Exclui um produto do Mercado Livre via API."""
    url = f"https://api.mercadolibre.com/items/{ml_product_id}"
    headers = {
        'Authorization': f'Bearer {MERCADO_LIVRE_ACCESS_TOKEN}'
    }
    try:
        response = requests.delete(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Erro ao excluir produto: {e}"}


def cadastrar_produto(request):
    """Função de cadastro de produto."""
    if request.method == 'POST':
        form = ProdutoFormComImagens(request.POST)
        arquivos = request.FILES.getlist('imagens')

        if form.is_valid():
            produto = form.save()

            # Salvar imagens associadas ao produto
            for imagem in arquivos:
                ImagemProduto.objects.create(produto=produto, imagem=imagem)

            # Publicar no Mercado Livre
            resposta_ml = publicar_no_mercado_livre(produto.id)

            # Verificar se a publicação foi bem-sucedida
            if 'id' in resposta_ml:
                messages.success(request, f'Produto cadastrado e sincronizado com o Mercado Livre! ID: {resposta_ml["id"]}')
            else:
                # Tratar caso a chave 'erro' esteja presente na resposta
                mensagem_erro = resposta_ml.get('erro', 'Erro desconhecido')
                messages.warning(request, f'Produto cadastrado, mas houve um erro no Mercado Livre: {mensagem_erro}')

            return redirect('cadastrar_produto')
    else:
        form = ProdutoFormComImagens()

    produtos = Produto.objects.all()
    q = request.GET.get('q', '')
    if q:
        produtos = Produto.objects.filter(descricao__icontains=q)

    return render(request, 'vendas/cadastrar_produto.html', {'form': form, 'produtos': produtos})

def editar_produto(request, pk):
    """Função de edição de produto."""
    produto = get_object_or_404(Produto, pk=pk)

    if request.method == 'POST':
        form = ProdutoFormComImagens(request.POST, request.FILES, instance=produto)
        arquivos = request.FILES.getlist('imagens')

        if form.is_valid():
            produto = form.save()

            # Salvar novas imagens
            for imagem in arquivos:
                ImagemProduto.objects.create(produto=produto, imagem=imagem)

            # Atualizar no Mercado Livre
            resposta_ml = publicar_no_mercado_livre(produto.id)

            if 'id' in resposta_ml:
                messages.success(request, f'Produto atualizado e sincronizado com o Mercado Livre! ID: {resposta_ml["id"]}')
            else:
                # Tratar caso a chave 'erro' esteja presente na resposta
                mensagem_erro = resposta_ml.get('erro', 'Erro desconhecido')
                messages.warning(request, f'Produto atualizado, mas houve um erro no Mercado Livre: {mensagem_erro}')

            return redirect('cadastrar_produto')

    else:
        form = ProdutoFormComImagens(instance=produto)

    imagens = produto.imagens.all()
    return render(request, 'vendas/editar_produto.html', {'form': form, 'produto': produto, 'imagens': imagens})

def excluir_produto(request, pk):
    """Função para excluir um produto."""
    produto = get_object_or_404(Produto, pk=pk)

    if request.method == 'POST':
        # Verifica se o produto tem código do Mercado Livre
        if produto.codigo_produto:
            resposta_ml = excluir_do_mercado_livre(produto.codigo_produto)

            if 'error' in resposta_ml:
                messages.warning(request, f'Houve um erro ao excluir do Mercado Livre: {resposta_ml}')
            else:
                messages.success(request, 'Produto excluído do Mercado Livre com sucesso!')
        else:
            messages.warning(request, 'Este produto não está sincronizado com o Mercado Livre.')

        # Excluir imagens e o produto do banco de dados
        produto.imagens.all().delete()
        produto.delete()
        messages.success(request, 'Produto e suas imagens foram excluídos do sistema!')

        return redirect('cadastrar_produto')

    return render(request, 'vendas/cadastrar_produto.html', {'produto': produto})

def excluir_imagem_produto(request, imagem_id):
    """Exclui uma imagem de produto."""
    imagem = get_object_or_404(ImagemProduto, id=imagem_id)
    produto_id = imagem.produto.pk

    imagem.delete()
    messages.success(request, 'Imagem excluída com sucesso!')

    return redirect('editar_produto', pk=produto_id)

#--------------------------------------------------CADASTRO CLIENTES-------------------------------------------------------#

def cadastrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente cadastrado com sucesso!')
            return redirect('cadastrar_cliente')
    else:
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
#-----------------------------------------------Cadastro de vendedores-------------------------------------------------#

def cadastrar_vendedor(request):
    if request.method == 'POST':
        form = VendedorForm(request.POST)
        if form.is_valid():
            form.save()
    form = VendedorForm()
    vendedores = Vendedor.objects.all()
    q = request.GET.get('q', '')
    if q:
        vendedores = Vendedor.objects.filter(nome__icontains=q)
    return render(request, 'vendas/cadastrar_vendedor.html', {'form': form, 'vendedores': vendedores})


def editar_vendedor(request, pk):
    vendedor = get_object_or_404(Vendedor, pk=pk)
    if request.method == 'POST':
        form = VendedorForm(request.POST, instance=vendedor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vendedor editado com sucesso!')
            return redirect('cadastrar_vendedor')
    else:
        form = VendedorForm(instance=vendedor)
    return render(request, 'vendas/cadastrar_vendedor.html', {'form': form})


def excluir_vendedor(request, pk):
    vendedor = get_object_or_404(Vendedor, pk=pk)
    if request.method == 'POST':
        vendedor.delete()
        messages.success(request, 'Vendedor Excluido!')
        return redirect('cadastrar_vendedor')
    return render(request, 'vendas/cadastrar_vendedor.html', {'vendedor': vendedor})

#----------------------------------------------------TELA DE VENDAS----------------------------------------------------#

# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
from django.core.files.base import ContentFile
from xhtml2pdf import pisa
import uuid
from .models import Venda, Cliente, Produto, Vendedor
import pdfkit
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template.loader import get_template
from django.urls import reverse  # Adicionado para evitar erro no redirect
from django.core.exceptions import ObjectDoesNotExist
import pdfkit  # Para gerar PDF com pdfkit
import uuid
from .models import Venda, Cliente, Produto, Vendedor,ItemVenda
import json
def gerar_id_venda():
    return str(uuid.uuid4().int)[:11]

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponse
from .models import Cliente, Vendedor, Produto, Venda, ItemVenda

def cadastrar_venda(request):
    clientes = Cliente.objects.all()
    produtos = Produto.objects.all()
    vendedores = Vendedor.objects.all()

    if request.method == "POST":
        cliente_id = request.POST.get("cliente")
        vendedor_id = request.POST.get("vendedor")
        forma_pagamento = request.POST.get("forma_pagamento")
        data_vencimento = request.POST.get("data_vencimento")
        desconto = request.POST.get("desconto", "0")
        acrescimo = request.POST.get("acrescimo", "0")

        # Validação: A data de vencimento é obrigatória somente se a forma de pagamento for 'conta_cliente'
        if forma_pagamento == 'conta_cliente' and not data_vencimento:
            return HttpResponse("O campo Data de Vencimento é obrigatório quando a forma de pagamento é 'Conta Cliente'.", status=400)
        
        if forma_pagamento not in [choice[0] for choice in Venda._meta.get_field('forma_pagamento').choices]:
            return HttpResponse("Forma de pagamento inválida.", status=400)



        try:
            desconto = Decimal(str(desconto)) if desconto else Decimal("0")
            acrescimo = Decimal(str(acrescimo)) if acrescimo else Decimal("0")
        except ValueError:
            return HttpResponse("Desconto ou Acréscimo inválido.", status=400)

        cliente = get_object_or_404(Cliente, id=cliente_id)
        vendedor = get_object_or_404(Vendedor, id=vendedor_id) if vendedor_id else None

        # Criação da venda
        venda = Venda.objects.create(
            cliente=cliente,
            vendedor=vendedor,
            forma_pagamento=forma_pagamento,
            desconto=desconto,
            acrescimo=acrescimo,
            total=Decimal("0"),
            data_vencimento=data_vencimento if forma_pagamento == 'conta_cliente' else None
        )

        total = Decimal("0")

        # Processando os produtos e quantidades enviados no formulário
        try:
            produtos_ids = json.loads(request.POST.get("produtos", "[]"))
            quantidades = json.loads(request.POST.get("quantidades", "[]"))
        except json.JSONDecodeError:
            return HttpResponse("Erro ao processar a lista de produtos.", status=400)

        if not produtos_ids or not quantidades or len(produtos_ids) != len(quantidades):
            return HttpResponse("Erro: Nenhum produto foi enviado ou os dados são inconsistentes.", status=400)

        # Criando os itens da venda
        for produto_id, quantidade in zip(produtos_ids, quantidades):
            try:
                produto = Produto.objects.get(id=int(produto_id))
                quantidade = int(quantidade)
                subtotal = Decimal(quantidade) * produto.preco

                ItemVenda.objects.create(
                    venda=venda,
                    produto=produto,
                    quantidade=quantidade,
                    preco_unitario=produto.preco,
                    subtotal=subtotal
                )
                total += subtotal
            except (Produto.DoesNotExist, ValueError):
                return HttpResponse(f"Erro ao processar produto com ID {produto_id}.", status=400)

        # Calculando o total da venda (total = subtotal - desconto + acrescimo)
        venda.total = total - desconto + acrescimo
        venda.save()

        # Redirecionando para a página de finalizar venda
        return redirect(reverse("finalizar_venda", kwargs={"venda_id": venda.id}))

    return render(request, "vendas/cadastrar_venda.html", {
        "clientes": clientes,
        "produtos": produtos,
        "vendedores": vendedores
    })

def pesquisar_venda(request):
    venda = None
    itens = None

    if request.method == "POST":
        venda_id = request.POST.get("venda_id")

        if venda_id:
            try:
                itens = ItemVenda.objects.filter(venda__id=venda_id)
                

                if itens.exists():
                    venda = itens.first().venda
                    
                else:
                    print("Nenhuma venda encontrada!")

            except Exception as e:
                print(f"Erro ao buscar venda: {e}")
                venda = None  

    return render(request, "vendas/cadastrar_venda.html", {
        "venda": venda,
        "itens": itens,
        "clientes": Cliente.objects.all(),
        "produtos": Produto.objects.all(),
        "vendedores": Vendedor.objects.all(),
    })


def editar_venda(request, venda_id):
    venda = get_object_or_404(Venda, id=venda_id)
    itens = ItemVenda.objects.filter(venda=venda)

    if request.method == "POST":
        cliente_id = request.POST.get("cliente")
        vendedor_id = request.POST.get("vendedor")
        forma_pagamento = request.POST.get("forma_pagamento")
        data_vencimento = request.POST.get("data_vencimento")
        desconto = request.POST.get("desconto", "0")
        acrescimo = request.POST.get("acrescimo", "0")

        # Validação: A data de vencimento é obrigatória somente se a forma de pagamento for 'conta_cliente'
        if forma_pagamento == 'conta_cliente' and not data_vencimento:
            return HttpResponse("O campo Data de Vencimento é obrigatório quando a forma de pagamento é 'Conta Cliente'.", status=400)

        if forma_pagamento not in [choice[0] for choice in Venda._meta.get_field('forma_pagamento').choices]:
            return HttpResponse("Forma de pagamento inválida.", status=400)

        try:
            desconto = Decimal(str(desconto)) if desconto else Decimal("0")
            acrescimo = Decimal(str(acrescimo)) if acrescimo else Decimal("0")
        except ValueError:
            return HttpResponse("Desconto ou Acréscimo inválido.", status=400)

        cliente = get_object_or_404(Cliente, id=cliente_id)
        vendedor = get_object_or_404(Vendedor, id=vendedor_id) if vendedor_id else None

        # Atualizando os dados da venda
        venda.cliente = cliente
        venda.vendedor = vendedor
        venda.forma_pagamento = forma_pagamento
        venda.desconto = desconto
        venda.acrescimo = acrescimo

        if forma_pagamento == 'conta_cliente':
            data_vencimento = request.POST.get("data_vencimento")
            print("Data de vencimento:", data_vencimento)
            try:
                 data_vencimento = datetime.strptime(data_vencimento, '%Y-%m-%d')
            except ValueError:
                return HttpResponse("Data de vencimento inválida.", status=400)
            venda.data_vencimento = data_vencimento
        else:
            venda.data_vencimento = None

        venda.total = 0
        ItemVenda.objects.filter(venda=venda).delete()

        try:
            produtos_ids = json.loads(request.POST.get("produtos", "[]"))
            quantidades = json.loads(request.POST.get("quantidades", "[]"))
        except json.JSONDecodeError:
            return HttpResponse("Erro ao processar a lista de produtos.", status=400)

        if not produtos_ids or not quantidades or len(produtos_ids) != len(quantidades):
            return HttpResponse("Erro: Nenhum produto foi enviado ou os dados são inconsistentes.", status=400)

        # Criando os novos itens de venda
        for produto_id, quantidade in zip(produtos_ids, quantidades):
            try:
                produto = Produto.objects.get(id=int(produto_id))
                quantidade = int(quantidade)
                subtotal = Decimal(quantidade) * produto.preco
                ItemVenda.objects.create(
                    venda=venda,
                    produto=produto,
                    quantidade=quantidade,
                    preco_unitario=produto.preco,
                    subtotal=subtotal
                )
                venda.total += subtotal
            except (Produto.DoesNotExist, ValueError):
                continue

        # Calculando o total da venda (total = subtotal - desconto + acrescimo)
        venda.total = venda.total - venda.desconto + venda.acrescimo
        venda.save()

        return redirect(reverse("finalizar_venda", kwargs={"venda_id": venda.id}))

    return render(request, "vendas/cadastrar_venda.html", {
        "venda": venda,
        "itens": itens,
        "clientes": Cliente.objects.all(),
        "produtos": Produto.objects.all(),
        "vendedores": Vendedor.objects.all(),
    })


def finalizar_venda(request, venda_id):
    venda = get_object_or_404(Venda, id=venda_id)
    itens = ItemVenda.objects.filter(venda=venda)
    
    venda.save()

    return render(request, "vendas/finalizar_venda.html", {
        "venda": venda,
        "itens": itens
    })



def gerar_pdf_venda(request, venda_id):
    venda = get_object_or_404(Venda, id=venda_id)
    html = render_to_string("vendas/pdf_venda.html", {"venda": venda})
    
    options = {
        "page-size": "A4",
        "encoding": "UTF-8",
        "enable-local-file-access": None,
    }

    pdf = pdfkit.from_string(html, False, options=options)

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="venda_{venda.id_venda}.pdf"'
    
    return response
def limpar_campos_venda(request, venda_id):
    venda = get_object_or_404(Venda, id=venda_id)

    # Reseta os campos sem excluir a venda
    venda.desconto = 0
    venda.acrescimo = 0
    venda.forma_pagamento = ""
    venda.save()

    # Redireciona para a tela de cadastro de venda
    return redirect("cadastrar_venda")
#---------------------------------------RESUMO DE VENDAS----------------------------------------------#

def resumo_vendas(request):
    vendas = Venda.objects.all()
    pesquisa = request.GET.get('pesquisa')
    data_venda = request.GET.get('data_venda')
    forma_pagamento = request.GET.get('forma_pagamento')
    total = 0

    # Filtragem por pesquisa (cliente ou ID de venda)
    if pesquisa:
        vendas = vendas.filter(Q(cliente__nome__icontains=pesquisa) | Q(id__icontains=pesquisa))

    # Filtragem por data da venda
    if data_venda:
        data_venda_obj = datetime.strptime(data_venda, '%Y-%m-%d').date()
        vendas = vendas.filter(data_venda__date=data_venda_obj)

    # Filtragem por forma de pagamento
    if forma_pagamento:
        vendas = vendas.filter(forma_pagamento__icontains=forma_pagamento)

    # Geração do PDF (após a filtragem)
    if request.GET.get('imprimir'):
        venda_ids = request.GET.get('venda_ids', '').split(',')
        venda_ids = [int(x) for x in venda_ids if x]
        total = float(request.GET.get('total', 0))
        vendas_selecionadas = Venda.objects.filter(id__in=venda_ids)
        template = get_template('vendas/resumo_vendas_pdf.html')
        html = template.render({'vendas': vendas_selecionadas, 'total': total})
        config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
        pdf = pdfkit.from_string(html, False, configuration=config)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="resumo_vendas.pdf"'
        return response
    
    

    # Soma total das vendas para exibir na página
    for venda in vendas:
        total += venda.total

    return render(request, 'vendas/resumo_vendas.html', {'vendas': vendas, 'total': total})



#---------------------------------------NFE----------------------------------------------------#




def carregar_certificado():
    certificado = crypto.load_certificate(crypto.FILETYPE_PEM, open('certificado.pem', 'r').read())
    chave_privada = crypto.load_privatekey(crypto.FILETYPE_PEM, open('chave_privada.pem', 'r').read())
    return certificado, chave_privada

def gerar_nfe(request):
    if request.method == 'POST':
        form = NFeForm(request.POST)
        if form.is_valid():
            nfe = form.save()
            xml = gerar_xml_nfe(nfe)
            certificado, chave_privada = carregar_certificado()
            xml_assinado = assinar_xml(xml, certificado, chave_privada)
            return render(request, 'vendas/nfe.html', {'nfe': nfe, 'xml': xml, 'xml_assinado': xml_assinado})
    else:
        form = NFeForm()
    return render(request, 'vendas/nfe_form.html', {'form': form})

def gerar_xml_nfe(nfe):
    # gerar o XML da NF-e
    xml = Element('NFe')
    # outros elementos necessários
    return tostring(xml)

def assinar_xml(xml, certificado, chave_privada):
    # assinar o XML com o certificado digital
    assinatura = crypto.sign(certificado, xml, 'sha256')
    # Retornar o XML assinado
    return xml + '\n' + assinatura

def enviar_xml(request, pk):
    nfe = NFe.objects.get(pk=pk)
    xml = gerar_xml_nfe(nfe)
    certificado, chave_privada = carregar_certificado()
    xml_assinado = assinar_xml(xml, certificado, chave_privada)
    # enviar o XML para a Receita Federal
    return redirect('nfe_enviado')

def nfe_enviado(request):
    return render(request, 'vendas/nfe_enviado.html')



#--------------------------------------contas a pagar---------------------------------------------------#

def despesas(request):
    form = DespesaForm()
    filtro_pagamento = request.GET.get('status', '')

    

    if request.method == 'POST':
        filtro_pagamento = request.POST.get('status', '')
        despesas_ids = request.POST.getlist('despesas')

        if 'marcar_pago' in request.POST:
            Despesa.objects.filter(pk__in=despesas_ids).update(pago=True)
        elif 'marcar_nao_pago' in request.POST:
            Despesa.objects.filter(pk__in=despesas_ids).update(pago=False)
        elif 'excluir' in request.POST:
            Despesa.objects.filter(pk__in=despesas_ids).delete()
        else:
            form = DespesaForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('despesas')

    # Filtros de pesquisa
    despesas = Despesa.objects.all()
    if request.GET.get('data_vencimento'):
        data = request.GET.get('data_vencimento')
    try:
        data_formatada = datetime.strptime(data, '%Y-%m-%d').date()
        despesas = despesas.filter(data_vencimento__exact=data_formatada)
    except ValueError:
        pass
    except UnboundLocalError:
        pass# Evita erro se a data não estiver no formato correto

    # Filtragem por data de vencimento corrigida
    
    # Filtro por descrição
    if request.GET.get('descricao'):
        despesas = despesas.filter(descricao__icontains=request.GET.get('descricao'))

    # Filtro por status de pagamento (agora com a opção "Nenhuma")
    if filtro_pagamento == 'pagas':
        despesas = despesas.filter(pago=True)
    elif filtro_pagamento == 'nao_pagas':
        despesas = despesas.filter(pago=False)
    # Se "Nenhuma" ou vazio, não aplica filtro de pagamento

    soma_despesas = sum(despesa.valor for despesa in despesas)

    return render(request, 'vendas/despesas.html', {
        'form': form,
        'despesas': despesas,
        'soma_despesas': soma_despesas,
        'filtro_pagamento': filtro_pagamento,
        'data_formatada': data_formatada if 'data_formatada' in locals() else None
    })



#------------------------------------------------contas a receber---------------------------------------------------------#

def vendas_conta_cliente(request):
    vendas = Venda.objects.filter(forma_pagamento='conta_cliente')
    
    # Filtros
    data_vencimento = request.GET.get('data_vencimento')
    nome_cliente = request.GET.get('nome_cliente')
    codigo_cliente = request.GET.get('codigo_cliente')
    pago = request.GET.get('pago')  # Filtro por pago/não pago

    if data_vencimento:
        vendas = vendas.filter(data_vencimento=data_vencimento)
    if nome_cliente:
        vendas = vendas.filter(cliente__nome__icontains=nome_cliente)
    if codigo_cliente:
        vendas = vendas.filter(cliente__codigo_cliente__icontains=codigo_cliente)
    if pago in ['True', 'False']:  # Evita filtros vazios
        vendas = vendas.filter(pago=(pago == 'True'))

    total = sum(venda.total for venda in vendas)

    if request.POST:
        if 'marcar_pago' in request.POST:
            for venda in vendas:
                if f'venda_{venda.id}' in request.POST:
                    venda.pago = True
                    venda.save(update_fields=['pago'])
        elif 'marcar_nao_pago' in request.POST:
            for venda in vendas:
                if f'venda_{venda.id}' in request.POST:
                    venda.pago = False
                    venda.save(update_fields=['pago'])
        return redirect('vendas_conta_cliente')

    if request.GET.get('imprimir'):
        template = get_template('vendas/vendas_conta_cliente_pdf.html')
        html = template.render({'vendas': vendas, 'total': total})
        config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
        pdf = pdfkit.from_string(html, False, configuration=config)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="vendas_conta_cliente.pdf"'
        return response

    return render(request, 'vendas/vendas_conta_cliente.html', {'vendas': vendas, 'total': total, 'pago': pago})



#----------------------------------------------------------------------------------#


from django.shortcuts import render, get_object_or_404, HttpResponse
from .models import Venda, ItemVenda

def visualizar_nfce(request, venda_id):
    venda = get_object_or_404(Venda, id=venda_id)
    itens = ItemVenda.objects.filter(venda=venda)

    context = {
        "venda": venda,
        "itens": itens,
    }
    
    return render(request, "vendas/visualizar_nfce.html", context)

def emitir_nfce(request, venda_id):
    venda = get_object_or_404(Venda, id=venda_id)
    
    # Aqui você pode adicionar a lógica real para emitir a NFC-e
    return HttpResponse(f"NFC-e da Venda {venda.id} emitida com sucesso!")




#---------------------------------------------RELATORIOS-------------------------------------------------#


