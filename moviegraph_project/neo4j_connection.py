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


neo4j_conn = Neo4jConnection()