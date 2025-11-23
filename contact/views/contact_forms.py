from django.shortcuts import get_object_or_404, render, redirect
from contact.forms import ContactForm, EntradasForm, SaidasForm
from django.urls import reverse
from contact.models import Contact, Entradas, Saidas
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q



@login_required(login_url='contact:login')
def create(request):
    form_action = reverse('contact:create')

    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES)
        context = {
            'form': form,
            'form_action': form_action,
        }

        if form.is_valid():
            descricao = form.cleaned_data.get('descricao_do_produto')
            marca = form.cleaned_data.get('marca')
            categoria = form.cleaned_data.get('categoria')

            # Verifica se já existe um produto com os mesmos dados
            if Contact.objects.filter(
                descricao_do_produto=descricao,
                marca=marca,
                categoria=categoria,
                show=True
            ).exists():
                messages.error(request, 'Este produto já está cadastrado.')
                return render(request, 'contact/create.html', context)

            contact = form.save(commit=False)
            contact.show = True
            contact.save()
            messages.success(request, 'Registrado com sucesso.')
            return redirect('contact:estoque')

        return render(request, 'contact/create.html', context)

    context = {
        'form': ContactForm(),
        'form_action': form_action,
    }

    return render(request, 'contact/create.html', context)


@login_required(login_url='contact:login')
def update(request, contact_id):

    contact = get_object_or_404(
        Contact, pk=contact_id, show=True
    )
    form_action = reverse('contact:update', args=(contact_id,))

    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES, instance=contact)

        context = {
            'form': form,
            'form_action': form_action,
        }

        if form.is_valid():
            messages.success(request, 'Registrado com sucesso.')
            contact = form.save()
            return redirect('contact:estoque')

        return render(
            request,
            'contact/create.html',
            context
        )

    context = {
        'form': ContactForm(instance=contact),
        'form_action': form_action,
    }

    return render(
        request,
        'contact/create.html',
        context
    )
    
@login_required(login_url='contact:login')
def update_entradas(request, contact_id):

    entrada = get_object_or_404(
        Entradas, pk=contact_id, show=True
    )
    form_action = reverse('contact:update_entradas', args=(contact_id,))

    if request.method == 'POST':
        form = EntradasForm(request.POST, request.FILES, instance=entrada)

        context = {
            'form': form,
            'form_action': form_action,
        }

        if form.is_valid():
            messages.success(request, 'Registrado com sucesso.')
            contact = form.save()
            return redirect('contact:entradas')

        return render(
            request,
            'contact/create_entradas.html',
            context
        )

    context = {
        'form': EntradasForm(instance=entrada),
        'form_action': form_action,
    }

    return render(
        request,
        'contact/create_entradas.html',
        context
    )
    
@login_required(login_url='contact:login')
def update_saidas(request, contact_id):

    saida = get_object_or_404(
        Saidas, pk=contact_id, show=True
    )
    form_action = reverse('contact:update_saidas', args=(contact_id,))

    if request.method == 'POST':
        form = SaidasForm(request.POST, request.FILES, instance=saida)

        context = {
            'form': form,
            'form_action': form_action,
        }

        if form.is_valid():
            messages.success(request, 'Registrado com sucesso.')
            contact = form.save()
            return redirect('contact:saidas')

        return render(
            request,
            'contact/create_saidas.html',
            context
        )

    context = {
        'form': SaidasForm(instance=saida),
        'form_action': form_action,
    }

    return render(
        request,
        'contact/create_saidas.html',
        context
    )

@login_required(login_url='contact:login')
def create_entradas(request):
    form_action = reverse('contact:create_entradas')

    if request.method == 'POST':
        form = EntradasForm(request.POST, request.FILES)
        context = {
            'form': form,
            'form_action': form_action,
        }

        if form.is_valid():
            contact = form.save(commit=False)
            contact.show = True
            messages.success(request, 'Registrado com sucesso.')
            contact.save()
            return redirect('contact:entradas')

        return render(
            request,
            'contact/create_entradas.html',
            context
        )

    context = {
        'form': EntradasForm(),
        'form_action': form_action,
    }

    return render(
        request,
        'contact/create_entradas.html',
        context
    )
    
@login_required(login_url='contact:login')
def create_saidas(request):
    form_action = reverse('contact:create_saidas')

    if request.method == 'POST':
        form = SaidasForm(request.POST, request.FILES)
        context = {
            'form': form,
            'form_action': form_action,
        }

        if form.is_valid():
            saida = form.save(commit=False)
            saida.show = True

            # calcula o custo médio do produto relacionado
            produto = saida.descricao_do_produto  # ForeignKey para Contact
            entradas = produto.entradas.all()

            total_qtd = 0
            total_custo = 0.0
            for entrada in entradas:
                if entrada.qtd and entrada.preco_de_custo:
                    total_qtd += entrada.qtd
                    total_custo += entrada.qtd * entrada.preco_de_custo

            preco_medio_custo = total_custo / total_qtd if total_qtd > 0 else 0

            # grava o custo médio vigente no momento da saída
            saida.preco_de_custo_registrado = preco_medio_custo

            saida.save()
            messages.success(request, 'Saída registrada com sucesso.')
            return redirect('contact:saidas')

        return render(request, 'contact/create_saidas.html', context)

    context = {
        'form': SaidasForm(),
        'form_action': form_action,
    }
    return render(request, 'contact/create_saidas.html', context)
