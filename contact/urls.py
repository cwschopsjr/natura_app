from django.urls import path
from contact import views

app_name = 'contact'

urlpatterns = [
    path('search/', views.search, name='search'),
    path('', views.index, name='index'),
    path('estoque/', views.estoque, name='estoque'),
    path('entradas/', views.entradas, name='entradas'),

    # contact (CRUD)
    path('contact/<int:contact_id>/', views.contact, name='contact'),
    path('entradas/<int:pk>/', views.contact_entradas, name='contact_entradas'),
    path('contact/create/', views.create, name='create'),
    path('contact/create_entradas/', views.create_entradas, name='create_entradas'),
    path('contact/<int:contact_id>/update/', views.update, name='update'),
    path('entradas/<int:contact_id>/update/', views.update_entradas, name='update_entradas'),
    path('user/login/', views.login_view, name='login'),
    path('user/logout/', views.logout_view, name='logout'),
    path('user/create/', views.register, name='register'),
]
