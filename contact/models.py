from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from itertools import chain
from operator import attrgetter

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

    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, blank=True, null=True)
    descricao_do_produto = models.CharField(max_length=100, blank=True, null=True)
    preco_de_catalogo = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Preço de catálogo', blank=True, null=True)
    data_de_validade = models.DateField(default=timezone.now)
    anotacoes = models.TextField(blank=True, verbose_name='Anotações')
    show = models.BooleanField(default=True)
    picture = models.ImageField(blank=True, upload_to='pictures/%Y/%m/')
    created_date = models.DateTimeField(default=timezone.now)

    # 🔹 novos campos
    preco_medio_custo = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Preço médio de custo', blank=True, null=True)
    saldo_estoque = models.PositiveIntegerField(verbose_name='Saldo em estoque', blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.descricao_do_produto} {self.categoria} {self.marca}'


class Entradas(models.Model):
    class Meta:
        verbose_name = "Entrada"
        verbose_name_plural = "Entradas"

    data_de_entrada = models.DateTimeField(default=timezone.now)
    descricao_do_produto = models.ForeignKey(Contact, on_delete=models.SET_NULL, blank=True, null=True, related_name='entradas')
    qtd = models.PositiveIntegerField(verbose_name='Quantidade', blank=True, null=True)
    preco_de_custo = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Preço de custo unitário', blank=True, null=True)
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
    descricao_do_produto = models.ForeignKey(Contact, on_delete=models.SET_NULL, blank=True, null=True, related_name='saidas')
    qtd = models.PositiveIntegerField(verbose_name='Quantidade', blank=True, null=True)
    preco_de_venda = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Preço de venda total', blank=True, null=True)
    preco_de_custo_registrado = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Preço de custo na saída', blank=True, null=True)
    lucro = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Lucro', blank=True, null=True)
    forma_de_pagamento = models.CharField(choices=pgto_choices, max_length=50, verbose_name='Forma de pagamento')
    cliente = models.CharField(max_length=50, verbose_name='Cliente')
    show = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f'{self.descricao_do_produto}'

    def save(self, *args, **kwargs):
        if self.descricao_do_produto and self.qtd:
            custo_unitario = self.descricao_do_produto.preco_medio_custo or 0
            self.preco_de_custo_registrado = custo_unitario
            
            if self.preco_de_venda is not None and self.qtd > 0:
                preco_unitario_venda = self.preco_de_venda / self.qtd
                self.lucro = (preco_unitario_venda - custo_unitario) * self.qtd
            else:
                self.lucro = 0
                
        super().save(*args, **kwargs)


# ==========================================
# SIGNALS DE ATUALIZAÇÃO DE ESTOQUE
# ==========================================

def recalcular_estoque(produto):
    """
    Recalcula o Saldo e Custo Médio usando a data real dos eventos.
    Em caso de empate de data/hora, processa as Entradas antes das Saídas.
    """
    if not produto:
        return

    entradas = list(produto.entradas.all())
    saidas = list(produto.saidas.all())

    for e in entradas:
        e.tipo_evento = 'entrada'
        e.data_evento = e.data_de_entrada
    for s in saidas:
        s.tipo_evento = 'saida'
        s.data_evento = s.data_de_saida

    # 🔹 O SEGREDO ESTÁ AQUI: Ordena pela data. 
    # Se a data for igual, Entrada (0) tem prioridade sobre Saída (1)
    eventos = sorted(chain(entradas, saidas), key=lambda x: (x.data_evento, 0 if x.tipo_evento == 'entrada' else 1))

    saldo = 0
    custo_medio = 0
    valor_total_investido = 0

    for evento in eventos:
        qtd = evento.qtd or 0
        if qtd == 0:
            continue

        if evento.tipo_evento == 'entrada':
            custo_unitario = evento.preco_de_custo or 0
            valor_total_investido += (qtd * custo_unitario)
            saldo += qtd
            
            if saldo > 0:
                custo_medio = valor_total_investido / saldo

        elif evento.tipo_evento == 'saida':
            saldo -= qtd
            
            # Se o estoque ZEROU, limpa a memória do custo antigo
            if saldo <= 0:
                saldo = 0
                valor_total_investido = 0
                custo_medio = 0
            else:
                valor_total_investido = saldo * custo_medio

    # Grava o resultado final no produto
    produto.saldo_estoque = saldo
    produto.preco_medio_custo = custo_medio
    produto.save(update_fields=['saldo_estoque', 'preco_medio_custo'])


@receiver([post_save, post_delete], sender=Entradas)
@receiver([post_save, post_delete], sender=Saidas)
def trigger_atualizacao_estoque(sender, instance, **kwargs):
    recalcular_estoque(instance.descricao_do_produto)