from django import forms
from .models import Produto, Cliente, Venda, Vendedor,Empresa, Despesa
from .models import NFe





class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = '__all__'


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ('codigo_produto','descricao', 'grupo', 'marca','unidade_medida','custo','preco','quantidade')



class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ('nome', 'cnpj','inscricao_estadual','cpf','rg','telefone','endereco','cep','numero','bairro','email')


class VendedorForm(forms.ModelForm):
    class Meta:
        model = Vendedor
        fields = ('nome_vendedor', 'codigo_vendedor')





class NFeForm(forms.ModelForm):
    class Meta:
        model = NFe
        fields = ('numero', 'serie', 'data_emissao')



class DespesaForm(forms.ModelForm):
    data_vencimento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%Y-%m-%d'])


    class Meta:
        model = Despesa
        fields = ('descricao', 'valor', 'data_vencimento')


