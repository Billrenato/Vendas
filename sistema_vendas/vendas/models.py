from django.db import models
from django.utils import timezone
import uuid

class Empresa(models.Model):
    nome_fantasia = models.CharField(max_length=255)
    razao_social = models.CharField(max_length=255)
    endereco = models.CharField(max_length=255)
    numero = models.CharField(max_length=20)
    bairro = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)
    cidade = models.CharField(max_length=100)
    complemento = models.CharField(max_length=255, blank=True)
    contato = models.CharField(max_length=100)
    inscricao_estadual = models.CharField(max_length=20)
    cnpj = models.CharField(max_length=20, unique=True)
    inscricao_municipal = models.CharField(max_length=20)
    cep = models.CharField(max_length=10)
    regime_tributario = models.CharField(max_length=100)
    dados_sintegra = models.CharField(max_length=255, blank=True)
    telefone = models.CharField(max_length=20)
    ibge_municipio = models.CharField(max_length=10)
    ibge_estado = models.CharField(max_length=10)

class Produto(models.Model):
    descricao = models.CharField(max_length=255)
    grupo = models.CharField(max_length=255)
    marca = models.CharField(max_length=255)
    unidade_medida = models.CharField(max_length=255)
    custo = models.DecimalField(max_digits=10, decimal_places=2)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    codigo_produto = models.CharField(max_length=255, blank=True, null=True)
    codigo_barras = models.CharField(max_length=50, blank=True, null=True)
    quantidade = models.IntegerField(default=0)
    quantidade_minima_venda = models.IntegerField(default=1)
    tamanho = models.CharField(max_length=255, blank=True, null=True)
    prod_cor = models.CharField(max_length=255, blank=True, null=True)
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True)
    material = models.CharField(max_length=255, blank=True, null=True)
    object_type = models.CharField(max_length=255, blank=True, null=True)
    

    CONDICOES = [
        ('novo', 'Novo'),
        ('usado', 'Usado'),
        ('recondicionado', 'Recondicionado'),
    ]
    condicao = models.CharField(max_length=20, choices=CONDICOES, default='novo')

    peso = models.DecimalField(max_digits=10, decimal_places=2, help_text="Peso em kg",blank=True, null=True)
    largura = models.DecimalField(max_digits=10, decimal_places=2, help_text="Largura em cm",blank=True, null=True)
    altura = models.DecimalField(max_digits=10, decimal_places=2, help_text="Altura em cm",blank=True, null=True)
    profundidade = models.DecimalField(max_digits=10, decimal_places=2, help_text="Profundidade em cm",blank=True, null=True)

    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('pausado', 'Pausado'),
        ('finalizado', 'Finalizado'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativo')

    link_mercado_livre = models.URLField(blank=True, null=True)
    mercado_livre_id = models.CharField(max_length=255, blank=True, null=True)

    TIPOS_ENVIO = [
        ('mercado_envios', 'Mercado Envios'),
        ('frete_proprio', 'Frete Próprio'),
        ('retirada', 'Retirada em mãos'),
    ]
    tipo_envio = models.CharField(max_length=20, choices=TIPOS_ENVIO, default='mercado_envios')

    envio_gratis = models.BooleanField(default=False)
    cobertura_frete = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Quanto do frete o vendedor cobre (se aplicável)")

    cep_origem = models.CharField(max_length=9, blank=True, null=True, help_text="CEP da origem do envio")
    metodos_envio_proprio = models.TextField(blank=True, null=True, help_text="Descrição dos métodos de envio próprio disponíveis")

    def reduzir_estoque(self, quantidade):
        if self.quantidade >= quantidade:
            self.quantidade -= quantidade
            self.save()
        else:
            raise ValueError(f"Estoque insuficiente para {self.descricao}")

    def __str__(self):
        return self.descricao
    


class ImagemProduto(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='imagens')
    imagem = models.ImageField(upload_to='produtos/')

    def __str__(self):
        return f"Imagem de {self.produto.descricao}"
    


class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=255)
    inscricao_estadual = models.CharField(max_length=255)
    cpf = models.CharField(max_length=255)
    rg = models.CharField(max_length=255)
    telefone = models.CharField(max_length=255)
    endereco = models.CharField(max_length=255)
    cep = models.CharField(max_length=255)
    numero = models.CharField(max_length=255)
    bairro = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    codigo_cliente = models.CharField(max_length=6, default=uuid.uuid4().hex[:6], editable=False)

class Vendedor(models.Model):
    nome_vendedor = models.CharField(max_length=255)
    codigo_vendedor = models.CharField(max_length=255)

    def __str__(self):
        return self.nome_vendedor

def gerar_id_venda():
    return str(uuid.uuid4().int)[:11]

class Venda(models.Model):
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    data_venda = models.DateTimeField(default=timezone.now)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    acrescimo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    id_venda = models.CharField(max_length=11, unique=True, default=gerar_id_venda)
    pago = models.BooleanField(default=False)
    forma_pagamento = models.CharField(max_length=20, choices=[
        ('dinheiro', 'Dinheiro'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('boleto', 'Boleto'),
        ('conta_cliente', 'Conta do Cliente')
    ])
    data_vencimento = models.DateField(null=True, blank=True)
    
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("finalizada", "Finalizada"),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pendente")
    def calcular_total(self):
        total = sum(item.subtotal for item in self.itens.all())
        self.total = total - self.desconto + self.acrescimo
        self.save()

    def __str__(self):
        return f"Venda {self.id_venda} - {self.cliente.nome}"

class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, blank=False, null=False)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.id:
            self.produto.reduzir_estoque(self.quantidade)
        self.subtotal = self.quantidade * self.preco_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantidade}x {self.produto.descricao} (Venda {self.venda.id_venda})"

class Despesa(models.Model):
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_cadastro = models.DateField(auto_now_add=True)
    data_vencimento = models.DateField()
    pago = models.BooleanField(default=False)

class Imposto(models.Model):
    icms = models.DecimalField(max_digits=10, decimal_places=2)
    ipi = models.DecimalField(max_digits=10, decimal_places=2)
    pis = models.DecimalField(max_digits=10, decimal_places=2)
    cofins = models.DecimalField(max_digits=10, decimal_places=2)
    cfop = models.DecimalField(max_digits=10, decimal_places=2)

class NFe(models.Model):
    numero = models.CharField(max_length=255)
    serie = models.CharField(max_length=255)
    data_emissao = models.DateField()
    emitente_nome = models.CharField(max_length=255)
    emitente_cnpj = models.CharField(max_length=255)
    emitente_endereco = models.CharField(max_length=255)
    destinatario_nome = models.CharField(max_length=255)
    destinatario_cnpj = models.CharField(max_length=255)
    destinatario_endereco = models.CharField(max_length=255)
    produtos = models.ManyToManyField(Produto)
    impostos = models.ManyToManyField(Imposto)
    forma_pagamento = models.CharField(max_length=255)
    transporte_modalidade = models.CharField(max_length=255)
    transporte_codigo = models.CharField(max_length=255)
    chave_acesso = models.CharField(max_length=255)