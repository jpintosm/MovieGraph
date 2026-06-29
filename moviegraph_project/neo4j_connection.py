from neo4j import GraphDatabase
from django.conf import settings


class Neo4jConnection:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )

    def query(self, cypher, parameters=None):
        with self.driver.session() as session:
            result = session.run(cypher, parameters or {})
            return [record.data() for record in result]
        

def crear_pelicula_neo4j(pelicula_id, pelicula):
    query = """
    MERGE (p:Pelicula {id: $id})
    SET p.titulo = $titulo,
        p.anio = $anio
    """

    neo4j_conn.query(query, {
        "id": str(pelicula_id),
        "titulo": pelicula["titulo"],
        "anio": pelicula["anio"]
    })

    for genero in pelicula["generos"]:
        neo4j_conn.query("""
        MATCH (p:Pelicula {id: $id})
        MERGE (g:Genero {nombre: $genero})
        MERGE (p)-[:PERTENECE_A]->(g)
        """, {
            "id": str(pelicula_id),
            "genero": genero.strip()
        })

    neo4j_conn.query("""
    MATCH (p:Pelicula {id: $id})
    MERGE (d:Director {nombre: $director})
    MERGE (d)-[:DIRIGIO]->(p)
    """, {
        "id": str(pelicula_id),
        "director": pelicula["director"].strip()
    })

    for actor in pelicula["actores"]:
        neo4j_conn.query("""
        MATCH (p:Pelicula {id: $id})
        MERGE (a:Actor {nombre: $actor})
        MERGE (a)-[:ACTUO_EN]->(p)
        """, {
            "id": str(pelicula_id),
            "actor": actor.strip()
        })

def actualizar_pelicula_neo4j(pelicula_id, pelicula):
    query = """
    MERGE (p:Pelicula {id: $id})
    SET p.titulo = $titulo,
        p.anio = $anio

    WITH p

    OPTIONAL MATCH (p)-[r1:PERTENECE_A]->(:Genero)
    DELETE r1

    WITH p

    OPTIONAL MATCH (:Director)-[r2:DIRIGIO]->(p)
    DELETE r2

    WITH p

    OPTIONAL MATCH (:Actor)-[r3:ACTUO_EN]->(p)
    DELETE r3
    """

    neo4j_conn.query(query, {
        "id": str(pelicula_id),
        "titulo": pelicula["titulo"],
        "anio": pelicula["anio"]
    })

    for genero in pelicula["generos"]:
        neo4j_conn.query("""
        MATCH (p:Pelicula {id: $id})
        MERGE (g:Genero {nombre: $genero})
        MERGE (p)-[:PERTENECE_A]->(g)
        """, {
            "id": str(pelicula_id),
            "genero": genero.strip()
        })

    neo4j_conn.query("""
    MATCH (p:Pelicula {id: $id})
    MERGE (d:Director {nombre: $director})
    MERGE (d)-[:DIRIGIO]->(p)
    """, {
        "id": str(pelicula_id),
        "director": pelicula["director"].strip()
    })

    for actor in pelicula["actores"]:
        neo4j_conn.query("""
        MATCH (p:Pelicula {id: $id})
        MERGE (a:Actor {nombre: $actor})
        MERGE (a)-[:ACTUO_EN]->(p)
        """, {
            "id": str(pelicula_id),
            "actor": actor.strip()
        })

def eliminar_pelicula_neo4j(pelicula_id):
    query = """
    MATCH (p:Pelicula {id: $id})
    DETACH DELETE p
    """

    neo4j_conn.query(query, {
        "id": str(pelicula_id)
    })

def obtener_peliculas_por_genero(genero):
    resultado = neo4j_conn.query("""
    MATCH (p:Pelicula)-[:PERTENECE_A]->(g:Genero {nombre: $genero})
    RETURN p.id AS id
    """, {"genero": genero})
    return [r["id"] for r in resultado]


def sincronizar_usuario_neo4j(usuario_id, usuario_nombre):
    neo4j_conn.query("""
    MERGE (u:Usuario {id: $id})
    SET u.nombre = $nombre
    """, {
        "id": str(usuario_id),
        "nombre": usuario_nombre or ""
    })

def agregar_reaccion(usuario_id, pelicula_id, tipo):
    # Eliminar reacción anterior si existe
    neo4j_conn.query("""
        MATCH (u:Usuario {id: $usuario_id})-[r]->(p:Pelicula {id: $pelicula_id})
        WHERE type(r) IN ['LE_GUSTA', 'NO_LE_GUSTA']
        DELETE r
        """, {"usuario_id": usuario_id, "pelicula_id": pelicula_id})
    
    # Crear nueva reacción
    if tipo == "gusta":
        neo4j_conn.query("""
        MERGE (u:Usuario {id: $usuario_id})
        MERGE (p:Pelicula {id: $pelicula_id})
        MERGE (u)-[:LE_GUSTA]->(p)
        """, {"usuario_id": usuario_id, "pelicula_id": pelicula_id})
    else:
        neo4j_conn.query("""
        MERGE (u:Usuario {id: $usuario_id})
        MERGE (p:Pelicula {id: $pelicula_id})
        MERGE (u)-[:NO_LE_GUSTA]->(p)
        """, {"usuario_id": usuario_id, "pelicula_id": pelicula_id})

def obtener_reaccion(usuario_id, pelicula_id):
    resultado = neo4j_conn.query("""
    MATCH (u:Usuario {id: $usuario_id})-[r]->(p:Pelicula {id: $pelicula_id})
    WHERE type(r) IN ['LE_GUSTA', 'NO_LE_GUSTA']
    RETURN type(r) AS tipo
    """, {"usuario_id": usuario_id, "pelicula_id": pelicula_id})
    
    if resultado:
        return "gusta" if resultado[0]["tipo"] == "LE_GUSTA" else "no_gusta"
    return None

neo4j_conn = Neo4jConnection()
