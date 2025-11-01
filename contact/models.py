from django.db import models
from django.utils import timezone
    
class Marca(models.Model):
    nome = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.nome

class Categoria(models.Model):
    nome = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.nome
    
class Contact(models.Model):
    class Meta:
        verbose_name = 'Produto'
        # unique_together = ('descricao_do_produto', 'marca', 'categoria')

    marca = models.ForeignKey(
        Marca,
        on_delete=models.SET_NULL,
        blank=True, null=True
    )
    
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        blank=True, null=True
    )
    
    descricao_do_produto = models.CharField(
        max_length=80, blank=True, null=True)
    # qtd = models.CharField(max_length=4, blank=True, null=True)
    # preco_de_custo = models.FloatField(verbose_name='Preço de custo', blank=True, null=True)
    preco_de_catalogo = models.FloatField(verbose_name='Preço de catálogo', blank=True, null=True)
    data_de_validade = models.DateField(default=timezone.now)
    anotacoes = models.TextField(blank=True, verbose_name='Anotações')
    show = models.BooleanField(default=True)
    picture = models.ImageField(blank=True, upload_to='pictures/%Y/%m/')
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f'{self.descricao_do_produto} {self.categoria} {self.marca} '

class Entradas(models.Model):
    data_de_entrada = models.DateTimeField(default=timezone.now)
    descricao_do_produto = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        blank=True, null=True, related_name='entradas'
    )
    qtd = models.PositiveIntegerField(blank=True, null=True)
    preco_de_custo = models.FloatField(verbose_name='Preço de custo', blank=True, null=True)
    data_de_validade = models.DateTimeField(default=timezone.now)
    show = models.BooleanField(default=True)
    
    def __str__(self) -> str:
        return f'{self.descricao_do_produto}'