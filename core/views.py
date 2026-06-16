from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from .db import usuarios, peliculas
import bcrypt
from datetime import datetime
from bson import ObjectId

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
        pelicula = {
            "titulo": request.POST.get("titulo"),
            "anio": int(request.POST.get("anio")),
            "generos": request.POST.get("generos").split(","),
            "director": request.POST.get("director"),
            "actores": request.POST.get("actores").split(","),
            "poster_url": request.POST.get("poster_url"),
            "resenas": []
        }
        peliculas.insert_one(pelicula)
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
    pelicula["_id"] = str(pelicula["_id"])
    if request.method == "POST":
        peliculas.update_one({"_id": ObjectId(id)}, {"$set": {
            "titulo": request.POST.get("titulo"),
            "anio": int(request.POST.get("anio")),
            "generos": request.POST.get("generos").split(","),
            "director": request.POST.get("director"),
            "actores": request.POST.get("actores").split(","),
            "poster_url": request.POST.get("poster_url"),
        }})
        return redirect("listar_peliculas")
    return render(request, "peliculas/editar.html", {"pelicula": pelicula})

def eliminar_pelicula(request, id):
    if login_requerido(request):
        return redirect("login")
    
    if request.session.get("usuario_rol") != "admin":
        return redirect("listar_peliculas")
    
    peliculas.delete_one({"_id": ObjectId(id)})
    return redirect("listar_peliculas")