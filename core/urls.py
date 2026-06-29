from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="login"), name="inicio"),
    path("registro/", views.registro, name="registro"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("peliculas/", views.listar_peliculas, name="listar_peliculas"),
    path("peliculas/nueva/", views.crear_pelicula, name="crear_pelicula"),
    path("peliculas/buscar-tmdb/", views.buscar_tmdb, name="buscar_tmdb"),
    path("peliculas/importar-tmdb/<int:tmdb_id>/", views.importar_tmdb, name="importar_tmdb"),
    path("peliculas/<str:id>/reaccion/<str:tipo>/", views.reaccionar_pelicula, name="reaccionar_pelicula"),
    path("peliculas/<str:id>/resena/", views.agregar_resena, name="agregar_resena"),
    path("peliculas/<str:id>/", views.detalle_pelicula, name="detalle_pelicula"),
    path("peliculas/<str:id>/editar/", views.editar_pelicula, name="editar_pelicula"),
    path("peliculas/<str:id>/eliminar/", views.eliminar_pelicula, name="eliminar_pelicula"),
    path("historial/", views.historial, name="historial"),
]