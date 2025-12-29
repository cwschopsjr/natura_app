from django.contrib import admin
from contact import models

@admin.register(models.Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = 'nome',
    ordering = '-id',
    
@admin.register(models.Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = 'nome',
    ordering = '-id',

@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = 'descricao_do_produto', 'marca', 'categoria', 'preco_de_custo', 'preco_de_catalogo', 'data_de_validade', 'show'
    ordering = '-id',
    search_fields = 'id', 'descricao_do_produto', 'marca__nome', 'categoria__nome', 'preco_de_catalogo', 'data_de_validade'
    list_per_page = 300
    list_max_show_all = 300
    list_editable = 'show',
    list_display_links = 'descricao_do_produto',
    
    def preco_de_custo(self, obj):
        entrada = obj.entradas.order_by('-data_de_entrada').first()
        if entrada and entrada.preco_de_custo is not None:
            return entrada.preco_de_custo
        return "-"
    preco_de_custo.short_description = "Preço de Custo"
    preco_de_custo.admin_order_field = 'entradas__preco_de_custo'

    
@admin.register(models.Entradas)
class EntradasAdmin(admin.ModelAdmin):
    list_display = 'data_de_entrada', 'produto_nome', 'qtd', 'preco_de_custo', 'data_de_validade', 'show'
    ordering = '-id',
    search_fields = 'data_de_entrada', 'id', 'descricao_do_produto__descricao_do_produto', 'qtd', 'preco_de_custo'
    list_per_page = 300
    list_max_show_all = 300
    list_editable = 'show',
    list_display_links = 'produto_nome',
    
    @admin.display(description="Descrição do Produto", ordering='descricao_do_produto__descricao_do_produto')
    def produto_nome(self, obj):
        return obj.descricao_do_produto.descricao_do_produto if obj.descricao_do_produto else "-"


    
@admin.register(models.Saidas)
class SaidasAdmin(admin.ModelAdmin):
    list_display = 'data_de_saida', 'produto_nome', 'qtd', 'preco_de_venda', 'forma_de_pagamento', 'cliente', 'show'
    ordering = '-id',
    search_fields = 'data_de_saida', 'id', 'descricao_do_produto__descricao_do_produto', 'qtd', 'preco_de_venda'
    list_per_page = 300
    list_max_show_all = 300
    list_editable = 'show',
    list_display_links = 'produto_nome',
    
    @admin.display(description="Descrição do Produto", ordering='descricao_do_produto__descricao_do_produto')
    def produto_nome(self, obj):
        return obj.descricao_do_produto.descricao_do_produto if obj.descricao_do_produto else "-"

