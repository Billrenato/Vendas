from django import forms
from .models import Produto, Cliente, Venda

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ('descricao', 'grupo', 'marca','unidade_medida','custo','preco')

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ('nome', 'cnpj','inscricao_estadual','cpf','rg','telefone','endereco','cep','numero','bairro','email')

##class VendaForm(forms.ModelForm):
    #class Meta:
        #model = Venda
        #fields = ('produto', 'cliente', 'data_venda', 'quantidade','total')
        
class VendaForm(forms.ModelForm):
    class Meta:
        model = Venda
        fields = ('produto', 'cliente', 'quantidade', 'total')
