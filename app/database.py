from neo4j import GraphDatabase
from app.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def get_session():
    return driver.session(database=NEO4J_DATABASE)

def close_driver():
    driver.close()