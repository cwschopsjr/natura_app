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
    descricao_do_produto = models.CharField(max_length=100, blank=True, null=True)
    preco_de_catalogo = models.FloatField(verbose_name='Preço de catálogo', blank=True, null=True)
    data_de_validade = models.DateField(default=timezone.now)
    anotacoes = models.TextField(blank=True, verbose_name='Anotações')
    show = models.BooleanField(default=True)
    picture = models.ImageField(blank=True, upload_to='pictures/%Y/%m/')
    created_date = models.DateTimeField(default=timezone.now)

    # 🔹 novos campos
    preco_medio_custo = models.FloatField(verbose_name='Preço médio de custo', blank=True, null=True)
    saldo_estoque = models.PositiveIntegerField(verbose_name='Saldo em estoque', blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.descricao_do_produto} {self.categoria} {self.marca}'

class Entradas(models.Model):
    class Meta:
        verbose_name = "Entrada"
        verbose_name_plural = "Entradas"

    data_de_entrada = models.DateTimeField(default=timezone.now)
    descricao_do_produto = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='entradas'
    )
    qtd = models.PositiveIntegerField(verbose_name='Quantidade', blank=True, null=True)
    preco_de_custo = models.FloatField(verbose_name='Preço de custo', blank=True, null=True)
    data_de_validade = models.DateField(default=timezone.now)
    show = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f'{self.descricao_do_produto}'

    def save(self, *args, **kwargs):
        # primeiro salva a entrada normalmente
        super().save(*args, **kwargs)

        # só recalcula se houver produto associado
        if self.descricao_do_produto:
            entradas = self.descricao_do_produto.entradas.all()
            saidas = self.descricao_do_produto.saidas.all()

            total_qtd = sum(e.qtd or 0 for e in entradas)
            total_custo = sum((e.qtd or 0) * (e.preco_de_custo or 0) for e in entradas)
            total_saidas = sum(s.qtd or 0 for s in saidas)

            preco_medio = total_custo / total_qtd if total_qtd > 0 else 0
            saldo = max(total_qtd - total_saidas, 0)  # 🔹 nunca negativo

            # atualiza os campos no Contact
            self.descricao_do_produto.preco_medio_custo = preco_medio
            self.descricao_do_produto.saldo_estoque = saldo
            self.descricao_do_produto.save(update_fields=['preco_medio_custo', 'saldo_estoque'])
    
from django.db import models
from django.utils import timezone
from contact.models import Contact

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
    preco_de_venda = models.FloatField(verbose_name='Preço de venda total', blank=True, null=True)
    preco_de_custo_registrado = models.FloatField(verbose_name='Preço de custo na saída', blank=True, null=True)
    lucro = models.FloatField(verbose_name='Lucro', blank=True, null=True)
    forma_de_pagamento = models.CharField(choices=pgto_choices, max_length=50, verbose_name='Forma de pagamento')
    cliente = models.CharField(max_length=50, verbose_name='Cliente')
    show = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f'{self.descricao_do_produto}'

    def save(self, *args, **kwargs):
        if self.descricao_do_produto and self.qtd:
            # 🔹 recalcula custo médio com base nas entradas
            entradas = self.descricao_do_produto.entradas.all()
            total_qtd = sum(e.qtd or 0 for e in entradas)
            total_custo = sum((e.qtd or 0) * (e.preco_de_custo or 0) for e in entradas)
            custo_unitario = total_custo / total_qtd if total_qtd > 0 else 0

            self.preco_de_custo_registrado = custo_unitario

            # 🔹 calcula lucro considerando preco_de_venda como TOTAL
            if self.preco_de_venda is not None and self.qtd > 0:
                preco_unitario_venda = self.preco_de_venda / self.qtd
                self.lucro = (preco_unitario_venda - custo_unitario) * self.qtd
            else:
                self.lucro = 0

            # 🔹 atualiza saldo de estoque
            saidas = self.descricao_do_produto.saidas.exclude(pk=self.pk).all()
            total_saidas = sum(s.qtd or 0 for s in saidas) + (self.qtd or 0)
            saldo = max(total_qtd - total_saidas, 0)

            self.descricao_do_produto.saldo_estoque = saldo
            self.descricao_do_produto.save(update_fields=['saldo_estoque'])

        super().save(*args, **kwargs)

