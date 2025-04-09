from neo4j import GraphDatabase
import json


NEO4J_URI = "bolt://localhost:7687"  
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neo4j"  


driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


with open('dblp.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

def paper_type_nodes_and_relationships(tx, paper):
    info = paper["info"]

    type = info.get("type")

    if type == 'Journal':
        tx.run(
            """
            MATCH (p:Paper {id:$paperid})
            MERGE (j:Journal {id: $event_id,name: $name})
            MERGE (p)-[:PUBLISHED_IN]->(j)
            """,
            paperid=info.get("paperid"),
            event_id=info.get("eventid"),
            name=info.get("event_name") 
        )
        tx.run(
            """
            MATCH (j:Journal {id:$eventid})
            MERGE (v:Volumen {volumen: $edition, year: $year, city:$city})
            MERGE (j)-[:IS_IN]->(v)
            """,
            eventid=info.get("eventid"),
            edition=info.get("edition"),
            year=info.get("year"),
            city=info.get("city")
        )
    if type == 'Conference' or type == 'Workshop'  :
        tx.run(
            """
            MATCH (p:Paper {id:$paperid})
            MERGE (c:Conference {id: $event_id,name: $name})
            MERGE (p)-[:PUBLISHED_IN]->(c)
            """,
            paperid=info.get("paperid"),
            event_id=info.get("eventid"),
            name=info.get("event_name") 
        )
        tx.run(
            """
            MATCH (c:Conference {id:$eventid})
            MERGE (e:Edition {edition: $edition,year: $year,venue:$city})
            MERGE (c)-[:BELONGS_TO]->(e)
            """,
            eventid=info.get("eventid"),
            edition=info.get("edition"),
            year=info.get("year"),
            city=info.get("city")
        )
        
             


def create_nodes_and_relationships(tx, paper):
    info = paper["info"]

    authors = info.get("authors", {}).get("author", [])
    reviewers = info.get("reviewers", {}).get("author", [])

    if isinstance(authors, dict):
        authors = [authors]


    main_author = authors[0] if authors else {"text": "unknown", "@pid": "0000"}
    main_author_name = main_author["text"]


    tx.run(
        """
        MERGE (p:Paper {id: $paperid, title: $title, type: $type,doi: $doi, main_author_name: $main_author_name, url: $url})
        """,
        paperid=info.get("paperid", 000),
        title=info.get("title", 'default'),
        doi=info.get("doi", 'default'),
        url=info.get("url", 'default'),
        type = info.get("type"),
        main_author_name=main_author_name
    ) 


    tx.run(
        """
        MERGE (a:Author {id: $author_id})
        ON CREATE SET a.name = $name 
        WITH a 
        MATCH (p:Paper {id: $paperid})
        MERGE (p)-[:WRITTEN_BY {position: $position}]->(a)
        """,
        author_id=main_author.get("@pid", 0000),
        name=main_author.get("text", 'default'),
        paperid=info.get("paperid", 0000),
        position=1
    )

    # Merge remaining Authors & Create Relationship with WITH Clause
    for position, author in enumerate(authors[1:], start=2):
        tx.run(
            """
            MERGE (a:Author {id: $author_id})
            ON CREATE SET a.name = $name 
            WITH a 
            MATCH (p:Paper {id: $paperid})
            MERGE (p)-[:WRITTEN_BY {position: $position}]->(a)
            """,
            author_id=author.get("@pid", 0000),
            name=author.get("text", 'default'),
            paperid=info.get("paperid", 0000),
            position=position
        )

     
    
    for position, reviewer in enumerate(reviewers, start=1):
        tx.run(
             """
            MERGE (r:Author {id: $reviewer_id})
            ON CREATE SET r.name = $reviewer_name
            WITH r
            MATCH (p:Paper {id: $paperid})
            MERGE (p)-[:REVIEWED_BY {position: $position}]->(r)
            """,
            reviewer_id=reviewer.get("@pid", 0000),
            reviewer_name=reviewer.get("text", 'default'),
            paperid=info.get("paperid", 0000),
            position=position
            )

    


    for cited_paper in info.get("cited", []):
        tx.run(
            """
            MATCH (p1:Paper {id: $paperid})
            MATCH (p2:Paper {id: $cited_id})
            MERGE (p1)-[:CITES]->(p2)
            """,
            paperid=info.get("paperid", 'default'),
            cited_id=cited_paper
        )
     
    
    for keyword in info.get("keywords", []):
        tx.run(
            """
            MATCH (p:Paper {id:$paperid})
            MERGE (k:Keyword {name: $keyword})
            MERGE (p)-[:HAS_KEYWORD]->(k)
            """,
            keyword=keyword,
            paperid=info.get("paperid")
        ) 
    paper_type_nodes_and_relationships(tx, paper)      
  

def main():
    with driver.session() as session:
        for paper in data["result"]["hits"].get("hit", []):
            session.write_transaction(create_nodes_and_relationships, paper)
    print("Data successfully imported into Neo4j!")

if __name__ == "__main__":
    main()
    driver.close()