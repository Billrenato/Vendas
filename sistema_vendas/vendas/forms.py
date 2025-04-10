from django import forms
from .models import Produto, Cliente, Venda, Vendedor,Empresa, Despesa,ImagemProduto
from .models import NFe





class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = '__all__'


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = (
            'codigo_produto','codigo_barras', 'descricao', 'grupo', 'marca', 'unidade_medida',
            'custo', 'preco', 'quantidade',
            'peso', 'largura', 'altura', 'profundidade',  
            'condicao', 'status', 'tipo_envio',  
            'imagem','tamanho','object_type','material','prod_cor',
            'cep_origem', 
            'cobertura_frete','envio_gratis',
        )

class ProdutoFormComImagens(forms.ModelForm):
    class Meta:
        model = Produto
        fields = [
            'descricao', 'grupo', 'marca', 'unidade_medida', 'custo', 'preco', 
            'codigo_produto','codigo_barras', 'quantidade',
            'peso', 'largura', 'altura', 'profundidade', 
            'condicao', 'status', 'tipo_envio','tamanho','object_type','material',
            'prod_cor','cep_origem',
            'cobertura_frete', 'envio_gratis'
        ]

class ImagemProdutoForm(forms.ModelForm):
    class Meta:
        model = ImagemProduto
        fields = ['imagem']

    class Meta:
        model = Produto
        fields = ['descricao', 'grupo', 'marca', 'unidade_medida', 'custo', 'preco', 'codigo_produto', 'quantidade']        

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


