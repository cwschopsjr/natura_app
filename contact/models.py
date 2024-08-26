from django.db import models
from django.utils import timezone


class Contact(models.Model):
    class Meta:
        verbose_name = 'Produto'

    marca = models.CharField(max_length=20, blank=True,
                             null=True, verbose_name='Marca')
    descricao_do_produto = models.CharField(
        max_length=80, blank=True, null=True)
    categoria = models.CharField(max_length=50, blank=True,
                                 null=True, verbose_name='Categoria')
    qtd = models.CharField(max_length=4, blank=True, null=True)
    preco = models.CharField(
        max_length=15, blank=True, verbose_name='Preço')
    anotacoes = models.TextField(blank=True, verbose_name='Anotações')
    show = models.BooleanField(default=True)
    enviar_arquivo = models.ImageField(blank=True, upload_to='pictures/%Y/%m/')
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f'{self.descricao_do_produto} {self.marca} {self.categoria}'
