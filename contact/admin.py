from django.contrib import admin
from contact import models

@admin.register(models.Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    ordering = ('nome',)
    
@admin.register(models.Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    ordering = ('nome',)

@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        'descricao_do_produto',
        'marca',
        'categoria',
        'quantidade_em_estoque',
        'preco_medio_custo',
        'preco_de_catalogo_formatado',
        'data_de_validade',
        'show',
    )
    ordering = ('descricao_do_produto',)
    search_fields = (
        'id',
        'descricao_do_produto',
        'marca__nome',
        'categoria__nome',
        'preco_de_catalogo',
        'data_de_validade',
    )
    list_per_page = 50
    list_max_show_all = 800
    list_editable = ('show',)
    list_display_links = ('descricao_do_produto',)

    @admin.display(description="Preço Médio de Custo")
    def preco_medio_custo(self, obj):
        entradas = list(obj.entradas.all().order_by('data_de_entrada'))
        saidas = list(obj.saidas.all().order_by('data_de_saida'))

        lotes = []
        for entrada in entradas:
            if entrada.qtd and entrada.preco_de_custo:
                lotes.append({"qtd": entrada.qtd, "preco": entrada.preco_de_custo})

        for saida in saidas:
            qtd_saida = saida.qtd or 0
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

        # 🔹 retorna string já formatada com 2 casas decimais
        return f"R$ {preco_medio_custo:.2f}"

    @admin.display(description="Quantidade em Estoque")
    def quantidade_em_estoque(self, obj):
        entradas = obj.entradas.all()
        saidas = obj.saidas.all()
        total_entrada = sum(e.qtd for e in entradas if e.qtd)
        total_saida = sum(s.qtd for s in saidas if s.qtd)
        saldo = total_entrada - total_saida
        return saldo if saldo >= 0 else 0

    @admin.display(description="Preço de Catálogo")
    def preco_de_catalogo_formatado(self, obj):
        if obj.preco_de_catalogo is not None:
            return f"R$ {float(obj.preco_de_catalogo):.2f}"
        return "-"

@admin.register(models.Entradas)
class EntradasAdmin(admin.ModelAdmin):
    list_display = ('data_de_entrada', 'produto_nome', 'qtd', 'preco_de_custo_formatado', 'show')
    ordering = ('-id',)
    search_fields = ('data_de_entrada', 'id', 'descricao_do_produto__descricao_do_produto', 'qtd', 'preco_de_custo')
    list_per_page = 50
    list_max_show_all = 300
    list_editable = ('show',)
    list_display_links = ('produto_nome',)
    
    @admin.display(description="Descrição do Produto", ordering='descricao_do_produto__descricao_do_produto')
    def produto_nome(self, obj):
        return obj.descricao_do_produto.descricao_do_produto if obj.descricao_do_produto else "-"

    @admin.display(description="Preço de Custo")
    def preco_de_custo_formatado(self, obj):
        if obj.preco_de_custo is not None:
            return f"R$ {float(obj.preco_de_custo):.2f}"
        return "-"

@admin.register(models.Saidas)
class SaidasAdmin(admin.ModelAdmin):
    list_display = (
        'data_de_saida',
        'produto_nome',
        'qtd',
        'preco_de_venda_formatado',
        'preco_de_custo_formatado',
        'lucro_formatado',
        'forma_de_pagamento',
        'cliente',
        'show',
    )
    ordering = ('-id',)
    search_fields = (
        'data_de_saida',
        'id',
        'descricao_do_produto__descricao_do_produto',
        'qtd',
        'cliente',
        'preco_de_venda',
    )
    list_per_page = 50
    list_max_show_all = 300
    list_editable = ('show',)
    list_display_links = ('produto_nome',)
    exclude = ('preco_de_custo_registrado', 'lucro')

    @admin.display(description="Descrição do Produto", ordering='descricao_do_produto__descricao_do_produto')
    def produto_nome(self, obj):
        return obj.descricao_do_produto.descricao_do_produto if obj.descricao_do_produto else "-"

    @admin.display(description="Preço de Venda")
    def preco_de_venda_formatado(self, obj):
        if obj.preco_de_venda is not None:
            return f"R$ {float(obj.preco_de_venda):.2f}"
        return "-"

    @admin.display(description="Preço de Custo Médio")
    def preco_de_custo_formatado(self, obj):
        if obj.preco_de_custo_registrado is not None:
            return f"R$ {float(obj.preco_de_custo_registrado):.2f}"
        return "-"

    @admin.display(description="Lucro")
    def lucro_formatado(self, obj):
        if obj.lucro is not None:
            return f"R$ {float(obj.lucro):.2f}"
        return "-"