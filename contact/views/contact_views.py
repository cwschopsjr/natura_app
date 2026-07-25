from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from datetime import datetime
from contact.models import Contact, Entradas, Saidas

def index(request):
    return render(request, 'contact/index.html', {})

def entradas(request):
    entradas = Entradas.objects.filter(show=True).order_by('-data_de_entrada')
    paginator = Paginator(entradas, 50)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'contact/entradas.html', {'page_obj': page_obj})

def saidas(request):
    saidas = Saidas.objects.filter(show=True).select_related('descricao_do_produto').order_by('-data_de_saida')
    paginator = Paginator(saidas, 50)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'contact/saidas.html', {'page_obj': page_obj})

def estoque(request):
    contacts = Contact.objects.filter(show=True).order_by('descricao_do_produto')
    paginator = Paginator(contacts, 50)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'contact/estoque.html', {'page_obj': page_obj, 'site_title': 'Produtos - '})

def contact(request, contact_id):
    single_contact = get_object_or_404(Contact, pk=contact_id, show=True)
    product_name = f'{single_contact.descricao_do_produto} - '
    return render(request, 'contact/contact.html', {'contact': single_contact, 'site_title': product_name})

def contact_entradas(request, pk):
    entrada = get_object_or_404(Entradas, pk=pk, show=True)
    produto = entrada.descricao_do_produto
    return render(request, 'contact/contact_entradas.html', {'entradas': entrada, 'produto': produto})

def contact_saidas(request, pk):
    saida = get_object_or_404(Saidas, pk=pk, show=True)
    produto = saida.descricao_do_produto
    return render(request, 'contact/contact_saidas.html', {'saidas': saida, 'produto': produto})

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
        # 🔹 recalcula custo médio e saldo com base nas entradas/saídas
        entradas = contact.entradas.all()
        saidas = contact.saidas.all()

        total_entradas = sum(e.qtd or 0 for e in entradas)
        total_custo = sum((e.qtd or 0) * (e.preco_de_custo or 0) for e in entradas)
        total_saidas = sum(s.qtd or 0 for s in saidas)

        saldo_estoque = max(total_entradas - total_saidas, 0)
        preco_medio = total_custo / total_entradas if total_entradas > 0 else 0

        # garante que os campos estejam preenchidos
        contact.saldo_estoque = saldo_estoque
        contact.preco_medio_custo = round(preco_medio, 2)

        match = False

        # Texto
        if search_value.lower() in str(contact.descricao_do_produto).lower():
            match = True
        elif contact.marca and search_value.lower() in str(contact.marca.nome).lower():
            match = True
        elif contact.categoria and search_value.lower() in str(contact.categoria.nome).lower():
            match = True

        # Quantidade
        if search_float is not None and saldo_estoque == int(search_float):
            match = True

        # Preço de catálogo
        if search_float is not None and contact.preco_de_catalogo is not None:
            if abs(contact.preco_de_catalogo - search_float) < 0.01:
                match = True

        # Preço médio de custo
        if search_float is not None and preco_medio is not None:
            if abs(preco_medio - search_float) < 0.01:
                match = True

        # Data de validade
        if search_date and contact.data_de_validade == search_date:
            match = True

        if match:
            results.append(contact)

    paginator = Paginator(results, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'contact/estoque.html', {
        'page_obj': page_obj,
        'site_title': 'Busca - '
    })

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

    entradas = Entradas.objects.filter(show=True).order_by('-id')
    results = []

    for entrada in entradas:
        match = False
        produto = entrada.descricao_do_produto

        if search_value.lower() in str(produto.descricao_do_produto).lower():
            match = True
        elif produto.marca and search_value.lower() in str(produto.marca.nome).lower():
            match = True
        elif produto.categoria and search_value.lower() in str(produto.categoria.nome).lower():
            match = True

        if search_float is not None and entrada.qtd == int(search_float):
            match = True

        if search_float is not None and entrada.preco_de_custo is not None:
            if abs(entrada.preco_de_custo - search_float) < 0.01:
                match = True

        if search_date and entrada.data_de_validade == search_date:
            match = True

        if match:
            results.append(entrada)

    paginator = Paginator(results, 500)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'contact/entradas.html', {'page_obj': page_obj, 'site_title': 'Busca - '})

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

    saidas = Saidas.objects.filter(show=True).order_by('-id')
    results = []

    for saida in saidas:
        match = False
        produto = saida.descricao_do_produto

        if search_value.lower() in str(produto.descricao_do_produto).lower():
            match = True
        elif produto.marca and search_value.lower() in str(produto.marca.nome).lower():
            match = True
        elif produto.categoria and search_value.lower() in str(produto.categoria.nome).lower():
            match = True

        if search_float is not None and saida.qtd == int(search_float):
            match = True

        if search_float is not None and saida.preco_de_venda is not None:
            if abs(saida.preco_de_venda - search_float) < 0.01:
                match = True

        if search_float is not None and saida.preco_de_custo_registrado is not None:
            if abs(saida.preco_de_custo_registrado - search_float) < 0.01:
                match = True

        if search_float is not None and saida.lucro is not None:
            if abs(saida.lucro - search_float) < 0.01:
                match = True

        if search_date and saida.data_de_saida.date() == search_date:
            match = True

        if match:
            results.append(saida)

    paginator = Paginator(results, 500)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'contact/saidas.html', {'page_obj': page_obj, 'site_title': 'Busca - '})