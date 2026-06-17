from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from .db import usuarios, peliculas
import bcrypt
from datetime import datetime
from bson import ObjectId
from moviegraph_project.neo4j_connection import crear_pelicula_neo4j, actualizar_pelicula_neo4j, eliminar_pelicula_neo4j
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

def normalizar_texto(texto):
    if not texto:
        return ""
    return texto.strip().upper()


def normalizar_lista(texto):
    if not texto:
        return []

    elementos = [
        item.strip().upper()
        for item in texto.split(",")
        if item.strip()
    ]

    # Elimina duplicados manteniendo el orden
    return list(dict.fromkeys(elementos))


def validar_anio(anio):
    anio = int(anio)

    if anio < 1888 or anio > 2027:
        raise ValueError("El año debe estar entre 1888 y 2027.")

    return anio

def validar_url_poster(url):
    if not url:
        return False

    url = url.strip()

    validador = URLValidator()

    try:
        validador(url)
    except ValidationError:
        return False

    extensiones_validas = (
        ".jpg",
        ".jpeg",
        ".png",
        ".webp"
    )

    return url.lower().endswith(extensiones_validas)

def login_requerido(request):
    return "usuario_id" not in request.session

def registro(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Verificar si el email ya existe
        if usuarios.find_one({"email": email}):
            messages.error(request, "El email ya está registrado")
            return redirect("registro")

        # Encriptar contraseña
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        # Guardar en MongoDB
        usuarios.insert_one({
            "nombre": nombre,
            "email": email,
            "password": password_hash,
            "fecha_registro": datetime.now(),
            "historial": [],
            "rol": "usuario"
        })

        messages.success(request, "Usuario registrado correctamente")
        return redirect("login")

    return render(request, "registro.html")

def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Buscar usuario en MongoDB
        usuario = usuarios.find_one({"email": email})

        if usuario and bcrypt.checkpw(password.encode("utf-8"), usuario["password"]):
            # Guardar sesión
            request.session["usuario_id"] = str(usuario["_id"])
            request.session["usuario_nombre"] = usuario["nombre"]
            request.session["usuario_rol"] = usuario.get("rol", "usuario")
            return redirect("listar_peliculas")
        else:
            messages.error(request, "Email o contraseña incorrectos")
            return redirect("login")

    return render(request, "login.html")


def logout(request):
    request.session.flush()
    return redirect("login")

def listar_peliculas(request):
    if login_requerido(request):
        return redirect("login")
    
    lista = list(peliculas.find())
    for p in lista:
        p["id"] = str(p["_id"])
    return render(request, "peliculas/listar.html", {"peliculas": lista})

def crear_pelicula(request):
    if login_requerido(request):
        return redirect("login")
    
    if request.session.get("usuario_rol") != "admin":
        return redirect("listar_peliculas")
    
    if request.method == "POST":
        titulo = normalizar_texto(request.POST.get("titulo"))
        anio = int(request.POST.get("anio"))
        generos = request.POST.getlist("generos")
        director = request.POST.get("director", "").strip()
        actores = request.POST.get("actores", "").strip()
        poster_url = request.POST.get("poster_url", "").strip()

        if (
            not titulo or
            not generos or
            not director or
            not actores or
            not poster_url or
            anio < 1888 or
            anio > 2026 or
            not validar_url_poster(poster_url)
        ):
            return render(request, "peliculas/crear.html")

        pelicula = {
            "titulo": titulo,
            "anio": anio,
            "generos": generos,
            "director": normalizar_texto(director),
            "actores": normalizar_lista(actores),
            "poster_url": poster_url,
            "resenas": []
        }

        resultado = peliculas.insert_one(pelicula)

        crear_pelicula_neo4j(str(resultado.inserted_id), pelicula)

        return redirect("listar_peliculas")

    return render(request, "peliculas/crear.html")

def detalle_pelicula(request, id):
    if login_requerido(request):
        return redirect("login")

    pelicula = peliculas.find_one({"_id": ObjectId(id)})
    pelicula["id"] = str(pelicula["_id"])
    return render(request, "peliculas/detalle.html", {"pelicula": pelicula})

def editar_pelicula(request, id):
    if login_requerido(request):
        return redirect("login")
    
    if request.session.get("usuario_rol") != "admin":
        return redirect("listar_peliculas")
    
    pelicula = peliculas.find_one({"_id": ObjectId(id)})

    if not pelicula:
        return redirect("listar_peliculas")

    pelicula["_id"] = str(pelicula["_id"])

    if request.method == "POST":
        titulo = normalizar_texto(request.POST.get("titulo"))
        anio = int(request.POST.get("anio"))
        generos = request.POST.getlist("generos")
        director = request.POST.get("director", "").strip()
        actores = request.POST.get("actores", "").strip()
        poster_url = request.POST.get("poster_url", "").strip()

        if (
            not titulo or
            not generos or
            not director or
            not actores or
            not poster_url or
            anio < 1888 or
            anio > 2026 or
            not validar_url_poster(poster_url)
        ):
            return render(request, "peliculas/editar.html", {"pelicula": pelicula})

        pelicula_actualizada = {
            "titulo": titulo,
            "anio": anio,
            "generos": generos,
            "director": normalizar_texto(director),
            "actores": normalizar_lista(actores),
            "poster_url": poster_url,
        }

        peliculas.update_one(
            {"_id": ObjectId(id)},
            {"$set": pelicula_actualizada}
        )

        actualizar_pelicula_neo4j(id, pelicula_actualizada)

        return redirect("listar_peliculas")

    return render(request, "peliculas/editar.html", {"pelicula": pelicula})

def eliminar_pelicula(request, id):
    if login_requerido(request):
        return redirect("login")
    
    if request.session.get("usuario_rol") != "admin":
        return redirect("listar_peliculas")

    peliculas.delete_one({"_id": ObjectId(id)})

    eliminar_pelicula_neo4j(id)

    return redirect("listar_peliculas")