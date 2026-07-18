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
        max_length=100, blank=True, null=True)
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
    lucro = models.FloatField(verbose_name='Lucro', blank=True, null=True)
    forma_de_pagamento = models.CharField(choices=pgto_choices, max_length=50, verbose_name='Forma de pagamento')
    cliente = models.CharField(max_length=50, verbose_name='Cliente')
    show = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f'{self.descricao_do_produto}'

    def save(self, *args, **kwargs):
        # calcula custo médio FIFO
        entradas = list(self.descricao_do_produto.entradas.all().order_by('data_de_entrada')) # type: ignore
        saidas = list(self.descricao_do_produto.saidas.exclude(pk=self.pk).all().order_by('data_de_saida')) # type: ignore

        lotes = []
        for entrada in entradas:
            if entrada.qtd and entrada.preco_de_custo:
                lotes.append({"qtd": entrada.qtd, "preco": entrada.preco_de_custo})

        for s in saidas:
            qtd_saida = s.qtd or 0
            while qtd_saida > 0 and lotes:
                lote = lotes[0]
                if lote["qtd"] > qtd_saida:
                    lote["qtd"] -= qtd_saida
                    qtd_saida = 0
                else:
                    qtd_saida -= lote["qtd"]
                    lotes.pop(0)

        saldo_estoque = sum(l["qtd"] for l in lotes)
        total_custo = sum(l["qtd"] * l["preco"] for l in lotes)
        preco_medio_custo = total_custo / saldo_estoque if saldo_estoque > 0 else 0

        # grava custo médio calculado
        self.preco_de_custo_registrado = round(preco_medio_custo, 2)

        # calcula lucro com base nesse custo
        if self.qtd and self.preco_de_venda:
            total_custo_saida = self.qtd * self.preco_de_custo_registrado
            self.lucro = (self.preco_de_venda * self.qtd) - total_custo_saida
        else:
            self.lucro = 0

        super().save(*args, **kwargs)


