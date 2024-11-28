import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv(verbose=True)

driver = GraphDatabase.driver(
    os.environ['NEO4J_URI'],
    auth=(os.environ['NEO4J_USER'], os.environ['NEO4J_PASSWORD'])
)
