from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q
from contact.models import Contact
from contact.models import Entradas
from django.db.models import Sum, F, FloatField, ExpressionWrapper
from django.db.models.functions import Coalesce



def index(request):

    context = {

    }

    return render(request, 'contact/index.html', context)

def entradas(request):
    entradas = Entradas.objects.filter(
        show=True).order_by('-descricao_do_produto')

    paginator = Paginator(entradas, 500)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }

    return render(request, 'contact/entradas.html', context)

def estoque(request):
    contacts = Contact.objects.filter(show=True).prefetch_related('entradas').order_by('-descricao_do_produto')

    for contact in contacts:
        entradas = contact.entradas.all() # type: ignore

        total_qtd = 0
        total_custo = 0.0

        for entrada in entradas:
            if entrada.qtd and entrada.preco_de_custo:
                total_qtd += entrada.qtd
                total_custo += entrada.qtd * entrada.preco_de_custo

        preco_medio = total_custo / total_qtd if total_qtd > 0 else 0

        setattr(contact, 'total_entradas', total_qtd)
        setattr(contact, 'preco_medio_custo', preco_medio)

    paginator = Paginator(contacts, 500)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'site_title': 'Produtos - '
    }

    return render(request, 'contact/estoque.html', context)

def contact(request, contact_id):
    single_contact = get_object_or_404(Contact, pk=contact_id, show=True)

    entradas = single_contact.entradas.all() # type: ignore

    total_qtd = 0
    total_custo = 0.0

    for entrada in entradas:
        if entrada.qtd and entrada.preco_de_custo:
            total_qtd += entrada.qtd
            total_custo += entrada.qtd * entrada.preco_de_custo

    preco_medio = total_custo / total_qtd if total_qtd > 0 else 0

    setattr(single_contact, 'total_entradas', total_qtd)
    setattr(single_contact, 'preco_medio_custo', preco_medio)

    product_name = f'{single_contact.descricao_do_produto} - '

    context = {
        'contact': single_contact,
        'site_title': product_name
    }

    return render(request, 'contact/contact.html', context)

def contact_entradas(request, pk):
    entrada = get_object_or_404(Entradas, pk=pk, show=True)

    produto = entrada.descricao_do_produto  # isso é o objeto Contact

    entradas_do_produto = produto.entradas.all() # type: ignore

    total_qtd = 0
    total_custo = 0.0

    for e in entradas_do_produto:
        if e.qtd and e.preco_de_custo:
            total_qtd += e.qtd
            total_custo += e.qtd * e.preco_de_custo

    preco_medio = total_custo / total_qtd if total_qtd > 0 else 0

    setattr(produto, 'total_entradas', total_qtd)
    setattr(produto, 'preco_medio_custo', preco_medio)

    context = {
        'entradas': entrada,
        'produto': produto,
    }

    return render(request, 'contact/contact_entradas.html', context)


def search(request):
    search_value = request.GET.get('q', '').strip()

    if search_value == '':
        return redirect('contact:estoque')

    contacts = Contact.objects\
        .filter(show=True)\
        .filter(Q(descricao_do_produto__icontains=search_value) |
                Q(qtd__icontains=search_value) |
                Q(preco_de_custo__icontains=search_value) |
                Q(data_de_entrada__icontains=search_value)) \
        .order_by('-id')

    paginator = Paginator(contacts, 500)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'site_title': 'Busca - '
    }

    return render(request, 'contact/estoque.html', context)
