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
    list_display = 'descricao_do_produto', 'marca', 'categoria', 'preco_de_catalogo', 'show'
    ordering = '-id',
    search_fields = 'id', 'descricao_do_produto', 'marca', 'categoria', 'preco_de_catalogo',
    list_per_page = 300
    list_max_show_all = 300
    list_editable = 'show',
    list_display_links = 'descricao_do_produto',
    
@admin.register(models.Entradas)
class EntradasAdmin(admin.ModelAdmin):
    list_display = 'data_de_entrada', 'descricao_do_produto__descricao_do_produto', 'qtd', 'preco_de_custo', 'data_de_validade', 'show'
    ordering = '-id',
    search_fields = 'data_de_entrada', 'id', 'descricao_do_produto__descricao_do_produto', 'qtd', 'preco_de_custo'
    list_per_page = 300
    list_max_show_all = 300
    list_editable = 'show',
    list_display_links = 'descricao_do_produto__descricao_do_produto',
    
@admin.register(models.Saidas)
class SaidasAdmin(admin.ModelAdmin):
    list_display = 'data_de_saida', 'descricao_do_produto__descricao_do_produto', 'qtd', 'preco_de_venda', 'forma_de_pagamento', 'cliente', 'show'
    ordering = '-id',
    search_fields = 'data_de_saida', 'id', 'descricao_do_produto__descricao_do_produto', 'qtd', 'preco_de_venda'
    list_per_page = 300
    list_max_show_all = 300
    list_editable = 'show',
    list_display_links = 'descricao_do_produto__descricao_do_produto',
