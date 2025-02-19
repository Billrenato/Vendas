from django.db import models
import uuid

def gerar_id_venda():
    return uuid.uuid4().hex

class Produto(models.Model):
    descricao = models.CharField(max_length=255)
    grupo = models.CharField(max_length=255)
    marca = models.CharField(max_length=255)
    unidade_medida = models.CharField(max_length=255)
    custo = models.DecimalField(max_digits=10, decimal_places=2)
    preco = models.DecimalField(max_digits=10, decimal_places=2)

class Cliente(models.Model):
    nome = models.CharField(max_length=255)
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

class Carrinho(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    quantidade = models.IntegerField(null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

class Venda(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    data_venda = models.DateField(auto_now_add=True)
    quantidade = models.IntegerField(default=1)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    id_venda = models.CharField(max_length=11, unique=True)

