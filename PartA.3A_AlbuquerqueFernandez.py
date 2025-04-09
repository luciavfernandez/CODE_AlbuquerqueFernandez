from neo4j import GraphDatabase
import json
import random
from synthetic_data import *


NEO4J_URI = "bolt://localhost:7687"  
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neo4j" 



driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def process_author(author):
  
    if isinstance(author, dict):
        return author.get("@pid", f"unknown_{random.randint(1000,9999)}"), author.get("text", "Unknown Author")
    return f"unknown_{random.randint(1000,9999)}", str(author)

def create_review_node(tx, paper):
    info = paper["info"]
    

    review_data = info.get("review", [])
    if review_data and isinstance(review_data, list) and len(review_data) > 0:
        review = review_data[0]
        if all(key in review for key in ['score', 'main_feedback', 'decision']):
            tx.run(
                """
                MATCH (p:Paper {id: $paperid})
                MERGE (r:Review {
                    score: $score,
                    main_feedback: $feedback,
                    decision: $decision
                })
                MERGE (p)-[:HAS]->(r)
                """,
                paperid=info.get("paperid"),
                score=review.get("score"),
                feedback=review.get("main_feedback"),
                decision=review.get("decision")
            )

 
    authors = info.get("authors", {}).get("author", [])
    if not isinstance(authors, list):
        authors = [authors] if authors else []
        
    for author in authors:
        author_id, author_name = process_author(author)
        affiliation = random.choice(affiliations)
        
        tx.run(
            """
            MERGE (a:Author {id: $author_id})
            ON CREATE SET a.name = $author_name
            WITH a
            MERGE (aff:Affiliation {name: $affiliation_name})
            SET aff.type = $affiliation_type
            MERGE (a)-[:AFFILIATED_WITH]->(aff)
            """,
            author_id=author_id,
            author_name=author_name,
            affiliation_name=affiliation["name"],
            affiliation_type=affiliation["type"]
        )

def main():

    with open('dblp.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    with driver.session() as session:
        for paper in data["result"]["hits"].get("hit", []):
            session.write_transaction(create_review_node, paper)
    print("Data successfully imported into Neo4j!")

if __name__ == "__main__":
    main()
    driver.close()