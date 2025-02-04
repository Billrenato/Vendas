from django.db import models

# Create your models here.
class Cliente(models.Model):
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.nome

class Produto(models.Model):
    nome = models.CharField(max_length=255)
    preco = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nome