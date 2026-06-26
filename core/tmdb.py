import requests
from django.conf import settings

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

def buscar_pelicula(titulo):
    url = f"{TMDB_BASE_URL}/search/movie"
    params = {
        "api_key": settings.TMDB_API_KEY,
        "query": titulo,
        "language": "es-ES"
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data.get("results", [])

def obtener_detalle_tmdb(tmdb_id):
    url = f"{TMDB_BASE_URL}/movie/{tmdb_id}"
    params = {
        "api_key": settings.TMDB_API_KEY,
        "language": "es-ES",
        "append_to_response": "credits"
    }
    response = requests.get(url, params=params)
    data = response.json()

    director = ""
    actores = []

    for persona in data.get("credits", {}).get("crew", []):
        if persona["job"] == "Director":
            director = persona["name"]
            break

    for actor in data.get("credits", {}).get("cast", [])[:5]:
        actores.append(actor["name"])

    return {
        "titulo": data.get("title", ""),
        "anio": int(data.get("release_date", "0000")[:4]),
        "generos": [g["name"] for g in data.get("genres", [])],
        "director": director,
        "actores": actores,
        "poster_url": TMDB_IMAGE_BASE_URL + data.get("poster_path", "") if data.get("poster_path") else ""
    }