from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["moviegraph"]

usuarios = db["usuarios"]
peliculas = db["peliculas"]