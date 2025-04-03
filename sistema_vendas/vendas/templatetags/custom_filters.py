from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(value, class_name):
    """
    Filtro para adicionar uma classe CSS ao campo do formulário.
    Exemplo: {{ form.descricao|add_class:"form-control" }}
    """
    return value.as_widget(attrs={"class": class_name})

