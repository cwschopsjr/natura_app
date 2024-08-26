from django.contrib import admin
from contact import models


@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = 'descricao_do_produto', 'marca', 'categoria', 'preco', 'qtd', 'show'
    ordering = '-id',
    # list_filter = 'last_name',
    search_fields = 'id', 'descricao_do_produto', 'marca', 'categoria', 'preco', 'qtd'
    list_per_page = 300
    list_max_show_all = 300
    list_editable = 'show',
    list_display_links = 'descricao_do_produto',


# @admin.register(models.Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = 'nome',
#     ordering = '-id',


# @admin.register(models.Category2)
# class Category2Admin(admin.ModelAdmin):
#     list_display = 'nome',
#     ordering = '-id',


# @admin.register(models.Units)
# class UnitsAdmin(admin.ModelAdmin):
#     list_display = 'nome',
#     ordering = '-id',
