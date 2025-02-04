from django.db import models

class Cliente(models.Model):
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.nome

class Produto(models.Model):
    nome = models.CharField(max_length=255)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.IntegerField(default=0)

    def __str__(self):
        return self.nome

class Venda(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField(default=1)
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Venda {self.id} - {self.cliente.nome} - {self.produto.nome}"

class Estoque(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField(default=0)

    def __str__(self):
        return f"Estoque {self.id} - {self.produto.nome}"