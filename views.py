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


def home(request):
    return render(request, 'vendas/home.html', {})




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

def cadastrar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto cadastrado com sucesso!')
            return redirect('cadastrar_produto')
    else:
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
                print(f"Itens encontrados: {itens}")  # <-- Adicionado para depuração

                if itens.exists():
                    venda = itens.first().venda
                    print(f"Venda encontrada: {venda}")  # <-- Adicionado para depuração
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
        venda.data_vencimento = data_vencimento if forma_pagamento == 'conta_cliente' else None

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
    data_inicial = request.GET.get('data_inicial')
    data_final = request.GET.get('data_final')
    total = 0
    
    if pesquisa:
        vendas = vendas.filter(Q(cliente__nome__icontains=pesquisa))
    
    if data_inicial and data_final:
        vendas = vendas.filter(data_venda__range=[data_inicial, data_final])
    
    if request.GET.get('imprimir'):
        template = get_template('vendas/resumo_vendas_pdf.html')
        html = template.render({'vendas': vendas})
        
        config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
        pdf = pdfkit.from_string(html, False, configuration=config)
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="resumo_vendas.pdf"'
        return response
    
    if request.POST:
        if 'somar' in request.POST:
            total = 0
            for venda in vendas:
                if 'venda_{}'.format(venda.id) in request.POST:
                    total += venda.total
            return render(request, 'vendas/resumo_vendas.html', {'vendas': vendas, 'total': total})
    
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
    if request.method == 'POST':
        if 'marcar_pago' in request.POST:
            despesas_ids = request.POST.getlist('despesas')
            for despesa_id in despesas_ids:
                despesa = Despesa.objects.get(pk=despesa_id)
                despesa.pago = True
                despesa.save()
        elif 'marcar_nao_pago' in request.POST:
            despesas_ids = request.POST.getlist('despesas')
            for despesa_id in despesas_ids:
                despesa = Despesa.objects.get(pk=despesa_id)
                despesa.pago = False
                despesa.save()
        elif 'imprimir_pdf' in request.POST:
            despesas = Despesa.objects.all()
            if request.GET.get('data'):
                despesas = despesas.filter(data_vencimento__gte=request.GET.get('data'))
            if request.GET.get('descricao'):
                despesas = despesas.filter(descricao__icontains=request.GET.get('descricao'))
            soma_despesas = 0
            for despesa in despesas:
                soma_despesas += despesa.valor
            template_path = 'vendas/despesas_pdf.html'
            context = {'despesas': despesas, 'soma_despesas': soma_despesas}
            template = get_template(template_path)
            html = template.render(context)
            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'no-outline': None
            }
            pdf = pdfkit.from_string(html, False, options=options)
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="despesas.pdf"'
            return response
        else:
            form = DespesaForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('despesas')
    despesas = Despesa.objects.all()
    if request.GET.get('data'):
        despesas = despesas.filter(data_vencimento__gte=request.GET.get('data'))
    if request.GET.get('descricao'):
        despesas = despesas.filter(descricao__icontains=request.GET.get('descricao'))
    soma_despesas = 0
    for despesa in despesas:
        soma_despesas += despesa.valor
    return render(request, 'vendas/despesas.html', {'form': form, 'despesas': despesas, 'soma_despesas': soma_despesas})

#------------------------------------------------contas a receber---------------------------------------------------------#


def vendas_conta_cliente(request):
    vendas = Venda.objects.filter(forma_pagamento='conta_cliente')
    total = 0
    
    if request.GET:
        data_vencimento = request.GET.get('data_vencimento')
        nome_cliente = request.GET.get('nome_cliente')
        codigo_cliente = request.GET.get('codigo_cliente')
        
        if data_vencimento:
            vendas = vendas.filter(data_vencimento=data_vencimento)
        if nome_cliente:
            vendas = vendas.filter(cliente__nome__icontains=nome_cliente)
        if codigo_cliente:
            vendas = vendas.filter(cliente__codigo_cliente__icontains=codigo_cliente)
    
    if request.POST:
        if 'marcar_pago' in request.POST:
            for venda in vendas:
                if 'venda_{}'.format(venda.id) in request.POST:
                    venda.pago = True
                    venda.save(update_fields=['pago'])
        elif 'marcar_nao_pago' in request.POST:
            for venda in vendas:
                if 'venda_{}'.format(venda.id) in request.POST:
                    venda.pago = False
                    venda.save(update_fields=['pago'])
        return redirect('vendas_conta_cliente')
    
    for venda in vendas:
        total += venda.total
    
    if request.GET.get('imprimir'):
        template = get_template('vendas/vendas_conta_cliente_pdf.html')
        html = template.render({'vendas': vendas})
        
        config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
        pdf = pdfkit.from_string(html, False, configuration=config)
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="vendas_conta_cliente.pdf"'
        return response
    
    return render(request, 'vendas/vendas_conta_cliente.html', {'vendas': vendas, 'total': total})

