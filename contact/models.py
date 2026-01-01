from django.db import models
from django.utils import timezone
    
class Marca(models.Model):
    
    class Meta:
        ordering = ['nome']
        
    nome = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.nome

class Categoria(models.Model):
    
    class Meta:
        verbose_name = "Categoria"          
        verbose_name_plural = "Categorias"
        ordering = ['nome']

    nome = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.nome
    
class Contact(models.Model):
    class Meta:
        verbose_name = 'Produto'
        ordering = ['descricao_do_produto']
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
    
    class Meta:
        verbose_name = "Entrada"          
        verbose_name_plural = "Entradas"
        
    data_de_entrada = models.DateTimeField(default=timezone.now)
    descricao_do_produto = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        blank=True, null=True, related_name='entradas'
    )
    qtd = models.PositiveIntegerField(verbose_name='Quantidade', blank=True, null=True)
    preco_de_custo = models.FloatField(verbose_name='Preço de custo', blank=True, null=True)
    data_de_validade = models.DateField(default=timezone.now)
    show = models.BooleanField(default=True)
    
    def __str__(self) -> str:
        return f'{self.descricao_do_produto}'
    
class Saidas(models.Model):
    
    class Meta:
        verbose_name = "Saída"          
        verbose_name_plural = "Saídas"
        
    pgto_choices = (
        ('Dinheiro', 'Dinheiro'),
        ('Cartão', 'Cartão'),
        ('PIX', 'PIX'),
        ('Shopee', 'Shopee'),
        ('Brinde', 'Brinde'),
        ('Troca', 'Troca'),
        ('Roubo', 'Roubo'),
        ('Quebrou', 'Quebrou'),
        ('Depósito', 'Depósito'),
        ('Casa', 'Casa'),
    )

    data_de_saida = models.DateTimeField(default=timezone.now)
    descricao_do_produto = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='saidas'
    )
    qtd = models.PositiveIntegerField(verbose_name='Quantidade', blank=True, null=True)
    preco_de_venda = models.FloatField(verbose_name='Preço de venda', blank=True, null=True)
    preco_de_custo_registrado = models.FloatField(verbose_name='Preço de custo na saída', blank=True, null=True)
    lucro = models.FloatField(verbose_name='Lucro', blank=True, null=True)  # <-- novo campo persistido
    forma_de_pagamento = models.CharField(choices=pgto_choices, max_length=50, verbose_name='Forma de pagamento')
    cliente = models.CharField(max_length=50, verbose_name='Cliente')
    show = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f'{self.descricao_do_produto}'

    def save(self, *args, **kwargs):
        """
        Calcula e salva o lucro no banco de dados
        sempre que a saída for criada ou atualizada.
        """
        if self.preco_de_venda and self.preco_de_custo_registrado is not None:
            self.lucro = self.preco_de_venda - self.preco_de_custo_registrado
        else:
            self.lucro = 0
        super().save(*args, **kwargs)

