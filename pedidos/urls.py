from django.urls import path
from . import views

urlpatterns = [
    path("", views.pedidos_home, name="pedidos_home"),
    path("ver/<str:pedido_id>/", views.pedido_detalle, name="pedido_detalle"),
    path("crear/", views.pedido_crear, name="pedido_crear"),
    path("editar/<str:pedido_id>/", views.pedido_editar, name="pedido_editar"),
    path("eliminar/<str:pedido_id>/", views.pedido_eliminar, name="pedido_eliminar"),

    # Nuevas secciones del menú
    path("clientes/", views.posibles_clientes, name="posibles_clientes"),
    path("gastos/", views.gastos, name="gastos"),
    path("resumen/", views.resumen, name="resumen"),
    path("configuracion/", views.configuracion, name="configuracion"),
]