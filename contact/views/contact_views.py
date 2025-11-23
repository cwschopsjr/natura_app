from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q
from django.db.models import Sum, F, FloatField, ExpressionWrapper
from datetime import datetime
from contact.models import Contact, Entradas, Saidas

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

def saidas(request):
    saidas = Saidas.objects.filter(show=True).select_related('descricao_do_produto').order_by('-descricao_do_produto')

    # calcular preço médio de custo apenas para exibir no produto
    for saida in saidas:
        entradas = saida.descricao_do_produto.entradas.all() #type: ignore
        total_qtd = 0
        total_custo = 0.0

        for entrada in entradas:
            if entrada.qtd and entrada.preco_de_custo:
                total_qtd += entrada.qtd
                total_custo += entrada.qtd * entrada.preco_de_custo

        preco_medio_custo = total_custo / total_qtd if total_qtd > 0 else 0
        setattr(saida.descricao_do_produto, 'preco_medio_custo', preco_medio_custo)

        # ❌ NÃO faça setattr(saida, 'lucro', ...)
        # O lucro já é calculado pela property no model

    paginator = Paginator(saidas, 500)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'contact/saidas.html', context)

def estoque(request):
    contacts = Contact.objects.filter(show=True).prefetch_related('entradas').order_by('-descricao_do_produto')

    for contact in contacts:
        entradas = contact.entradas.all() # type: ignore
        saidas = contact.saidas.all() # type: ignore

        total_entrada = 0
        total_saida = 0
        total_custo = 0.0

        for entrada in entradas:
            if entrada.qtd and entrada.preco_de_custo:
                total_entrada += entrada.qtd
                total_custo += entrada.qtd * entrada.preco_de_custo
        
        for saida in saidas:
            if saida.qtd:
                total_saida += saida.qtd

        preco_medio = total_custo / total_entrada if total_entrada > 0 else 0
        saldo_estoque = total_entrada - total_saida


        setattr(contact, 'total_entrada', total_entrada)
        setattr(contact, 'total_saida', total_saida)
        setattr(contact, 'saldo_estoque', saldo_estoque)
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

    entradas = single_contact.entradas.all()  # type: ignore
    saidas = single_contact.saidas.all()      # type: ignore

    total_entrada = 0
    total_saida = 0
    total_custo = 0.0

    # somatório das entradas
    for entrada in entradas:
        if entrada.qtd and entrada.preco_de_custo:
            total_entrada += entrada.qtd
            total_custo += entrada.qtd * entrada.preco_de_custo

    # somatório das saídas
    for saida in saidas:
        if saida.qtd:
            total_saida += saida.qtd

    # cálculos finais
    preco_medio = total_custo / total_entrada if total_entrada > 0 else 0
    saldo_estoque = total_entrada - total_saida

    # adicionando atributos ao objeto
    setattr(single_contact, 'total_entradas', total_entrada)
    setattr(single_contact, 'total_saidas', total_saida)
    setattr(single_contact, 'saldo_estoque', saldo_estoque)
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

def contact_saidas(request, pk):
    saida = get_object_or_404(Saidas, pk=pk, show=True)

    produto = saida.descricao_do_produto  # isso é o objeto Contact

    saidas_do_produto = produto.saidas.all() # type: ignore

    total_qtd = 0
    total_custo = 0.0

    for e in saidas_do_produto:
        if e.qtd and e.preco_de_venda:
            total_qtd += e.qtd
            total_custo += e.qtd * e.preco_de_venda

    preco_medio = total_custo / total_qtd if total_qtd > 0 else 0

    setattr(produto, 'total_saidas', total_qtd)
    setattr(produto, 'preco_medio_custo', preco_medio)

    context = {
        'saidas': saida,
        'produto': produto,
    }

    return render(request, 'contact/contact_saidas.html', context)

def search(request):
    search_value = request.GET.get('q', '').strip()

    if search_value == '':
        return redirect('contact:estoque')

    try:
        search_float = float(search_value.replace(',', '.'))
    except ValueError:
        search_float = None

    try:
        search_date = datetime.strptime(search_value, '%d/%m/%Y').date()
    except ValueError:
        search_date = None

    contacts = Contact.objects.filter(show=True).prefetch_related('entradas', 'saidas').order_by('-id')

    results = []
    for contact in contacts:
        entradas = contact.entradas.all() # type: ignore
        saidas = contact.saidas.all() # type: ignore

        total_entradas = sum(e.qtd for e in entradas if e.qtd)
        total_custo = sum(e.qtd * e.preco_de_custo for e in entradas if e.qtd and e.preco_de_custo)
        total_saidas = sum(s.qtd for s in saidas if s.qtd)

        preco_medio = total_custo / total_entradas if total_entradas > 0 else 0
        saldo_estoque = total_entradas - total_saidas
        valor_estoque = saldo_estoque * preco_medio

        setattr(contact, 'total_entradas', total_entradas)
        setattr(contact, 'total_saidas', total_saidas)
        setattr(contact, 'saldo_estoque', saldo_estoque)
        setattr(contact, 'preco_medio_custo', preco_medio)
        setattr(contact, 'valor_estoque', valor_estoque)

        match = False

        # Texto
        if search_value.lower() in str(contact.descricao_do_produto).lower():
            match = True
        elif search_value.lower() in str(contact.marca.nome).lower(): # type: ignore
            match = True
        elif search_value.lower() in str(contact.categoria.nome).lower(): # type: ignore
            match = True

        # Quantidade (saldo de estoque)
        if search_float is not None and saldo_estoque == int(search_float):
            match = True

        # Preço de catálogo
        if search_float is not None and contact.preco_de_catalogo is not None:
            if abs(contact.preco_de_catalogo - search_float) < 0.01:
                match = True

        # Preço médio de custo
        if search_float is not None:
            if abs(preco_medio - search_float) < 0.01:
                match = True

        # Preço de custo individual
        if search_float is not None:
            for entrada in entradas:
                if entrada.preco_de_custo is not None:
                    if abs(entrada.preco_de_custo - search_float) < 0.01:
                        match = True
                        break

        # Data de validade
        if search_value:
            for e in contacts:
                if e.data_de_validade:
                    if e.data_de_validade.strftime('%d/%m/%Y') == search_value:
                        match = True
                        break

        if match:
            results.append(contact)

    paginator = Paginator(results, 500)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'site_title': 'Busca - '
    }

    return render(request, 'contact/estoque.html', context)

def search_entradas(request):
    search_value = request.GET.get('q', '').strip()

    if search_value == '':
        return redirect('contact:entradas')

    try:
        search_float = float(search_value.replace(',', '.'))
    except ValueError:
        search_float = None

    try:
        search_date = datetime.strptime(search_value, '%d/%m/%Y').date()
    except ValueError:
        search_date = None

    contacts = Contact.objects.filter(show=True).prefetch_related('entradas', 'saidas').order_by('-id')

    results = []
    for contact in contacts:
        entradas = contact.entradas.all() # type: ignore
        saidas = contact.saidas.all() # type: ignore

        total_entradas = sum(e.qtd for e in entradas if e.qtd)
        total_custo = sum(e.qtd * e.preco_de_custo for e in entradas if e.qtd and e.preco_de_custo)
        total_saidas = sum(s.qtd for s in saidas if s.qtd)

        preco_medio = total_custo / total_entradas if total_entradas > 0 else 0
        saldo_estoque = total_entradas - total_saidas
        valor_estoque = saldo_estoque * preco_medio

        setattr(contact, 'total_entradas', total_entradas)
        setattr(contact, 'total_saidas', total_saidas)
        setattr(contact, 'saldo_estoque', saldo_estoque)
        setattr(contact, 'preco_medio_custo', preco_medio)
        setattr(contact, 'valor_estoque', valor_estoque)

        match = False

        # Texto
        if search_value.lower() in str(contact.descricao_do_produto).lower():
            match = True
        elif search_value.lower() in str(contact.marca.nome).lower(): # type: ignore
            match = True
        elif search_value.lower() in str(contact.categoria.nome).lower(): # type: ignore
            match = True

        # Quantidade (saldo de estoque)
        if search_float is not None and saldo_estoque == int(search_float):
            match = True

        # Preço de catálogo
        if search_float is not None and contact.preco_de_catalogo is not None:
            if abs(contact.preco_de_catalogo - search_float) < 0.01:
                match = True

        # Preço médio de custo
        if search_float is not None:
            if abs(preco_medio - search_float) < 0.01:
                match = True

        # Preço de custo individual
        if search_float is not None:
            for entrada in entradas:
                if entrada.preco_de_custo is not None:
                    if abs(entrada.preco_de_custo - search_float) < 0.01:
                        match = True
                        break

        # Data de validade
        if search_value:
            for e in contacts:
                if e.data_de_validade:
                    if e.data_de_validade.strftime('%d/%m/%Y') == search_value:
                        match = True
                        break

        if match:
            results.append(contact)

    paginator = Paginator(results, 500)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'site_title': 'Busca - '
    }

    return render(request, 'contact/entradas.html', context)

def search_saidas(request):
    search_value = request.GET.get('q', '').strip()

    if search_value == '':
        return redirect('contact:saidas')

    try:
        search_float = float(search_value.replace(',', '.'))
    except ValueError:
        search_float = None

    try:
        search_date = datetime.strptime(search_value, '%d/%m/%Y').date()
    except ValueError:
        search_date = None

    contacts = Contact.objects.filter(show=True).prefetch_related('entradas', 'saidas').order_by('-id')

    results = []
    for contact in contacts:
        entradas = contact.entradas.all() # type: ignore
        saidas = contact.saidas.all() # type: ignore

        total_entradas = sum(e.qtd for e in entradas if e.qtd)
        total_custo = sum(e.qtd * e.preco_de_custo for e in entradas if e.qtd and e.preco_de_custo)
        total_saidas = sum(s.qtd for s in saidas if s.qtd)

        preco_medio = total_custo / total_entradas if total_entradas > 0 else 0
        saldo_estoque = total_entradas - total_saidas
        valor_estoque = saldo_estoque * preco_medio

        setattr(contact, 'total_entradas', total_entradas)
        setattr(contact, 'total_saidas', total_saidas)
        setattr(contact, 'saldo_estoque', saldo_estoque)
        setattr(contact, 'preco_medio_custo', preco_medio)
        setattr(contact, 'valor_estoque', valor_estoque)

        match = False

        # Texto
        if search_value.lower() in str(contact.descricao_do_produto).lower():
            match = True
        elif search_value.lower() in str(contact.marca.nome).lower(): # type: ignore
            match = True
        elif search_value.lower() in str(contact.categoria.nome).lower(): # type: ignore
            match = True

        # Quantidade (saldo de estoque)
        if search_float is not None and saldo_estoque == int(search_float):
            match = True

        # Preço de catálogo
        if search_float is not None and contact.preco_de_catalogo is not None:
            if abs(contact.preco_de_catalogo - search_float) < 0.01:
                match = True

        # Preço médio de custo
        if search_float is not None:
            if abs(preco_medio - search_float) < 0.01:
                match = True

        # Preço de custo individual
        if search_float is not None:
            for entrada in entradas:
                if entrada.preco_de_custo is not None:
                    if abs(entrada.preco_de_custo - search_float) < 0.01:
                        match = True
                        break

        # Data de validade
        if search_value:
            for e in contacts:
                if e.data_de_validade:
                    if e.data_de_validade.strftime('%d/%m/%Y') == search_value:
                        match = True
                        break

        if match:
            results.append(contact)

    paginator = Paginator(results, 500)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'site_title': 'Busca - '
    }

    return render(request, 'contact/saidas.html', context)