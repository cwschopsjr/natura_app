from django.urls import path
from contact import views

app_name = 'contact'

urlpatterns = [
    path('search/', views.search, name='search'),
    path('', views.index, name='index'),
    path('estoque/', views.estoque, name='estoque'),
    path('entradas/', views.entradas, name='entradas'),
    path('saidas/', views.saidas, name='saidas'),

    # contact (CRUD)
    path('contact/<int:contact_id>/', views.contact, name='contact'),
    path('entradas/<int:pk>/', views.contact_entradas, name='contact_entradas'),
    path('saidas/<int:pk>/', views.contact_saidas, name='contact_saidas'),
    path('contact/create/', views.create, name='create'),
    path('contact/create_entradas/', views.create_entradas, name='create_entradas'),
    path('contact/create_saidas/', views.create_saidas, name='create_saidas'),
    path('contact/<int:contact_id>/update/', views.update, name='update'),
    path('entradas/<int:contact_id>/update/', views.update_entradas, name='update_entradas'),
    path('saidas/<int:contact_id>/update/', views.update_saidas, name='update_saidas'),
    path('user/login/', views.login_view, name='login'),
    path('user/logout/', views.logout_view, name='logout'),
    path('user/create/', views.register, name='register'),
]
