"""
URL configuration for imperyo project.

The `urlpatterns` list routes URLs to views.
More info:
https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


urlpatterns = [
    # Redirección automática desde "/" hacia "/pedidos/"
    path('', lambda request: redirect('/pedidos/')),

    # Rutas normales
    path('admin/', admin.site.urls),
    path('pedidos/', include('pedidos.urls')),
]
