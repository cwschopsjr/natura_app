from django.contrib import admin
from contact import models


@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = 'descricao_do_produto', 'marca', 'categoria', 'preco', 'qtd', 'show'
    ordering = '-id',
    search_fields = 'id', 'descricao_do_produto', 'marca', 'categoria', 'preco', 'qtd'
    list_per_page = 300
    list_max_show_all = 300
    list_editable = 'show',
    list_display_links = 'descricao_do_produto',
