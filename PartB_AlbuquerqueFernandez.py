from neo4j import GraphDatabase
import json

NEO4J_URI = "bolt://localhost:7687"  
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neo4j"

class Neo4jQueries:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def run_query(self, query, description, **kwargs):
        with self.driver.session() as session:
            print(f"\nRunning {description}")
            try:
                result = session.run(query, **kwargs)
                records = [record for record in result]
                return records
            except Exception as e:
                print(f" Error running query: {e}")
                return None

    def top_cited_papers(self):
        query = """
        MATCH (p:Paper)-[:PUBLISHED_IN]->(c:Conference)
        WHERE p.type IN ['Conference', 'Workshop']
        MATCH (p)-[:CITES]->(p1:Paper)
        WITH c, p, COUNT(p1) AS citationCount
        ORDER BY c.name, citationCount DESC
        WITH c, COLLECT({paper: p, citations: citationCount})[0..3] AS topPapers
        RETURN c.name AS eventName,
               [item IN topPapers | item.paper.title] AS topPaper,
               [item IN topPapers | item.citations] AS citationCounts
        ORDER BY citationCounts DESC
        """
        return self.run_query(query, "Query N1: Finding top 3 most cited papers per conference/workshop")

    def conference_communities(self):
        query = """
        MATCH (c:Conference)-[:BELONGS_TO]->(e:Edition)
        MATCH (c)<-[:PUBLISHED_IN]-(p:Paper)-[:WRITTEN_BY]->(a:Author)
        WHERE p.type IN ['Conference', 'Workshop']
        WITH c, a, COUNT(DISTINCT e) AS editionCount
        WHERE editionCount > 3
        WITH c, COLLECT(a.name) AS communityAuthors, editionCount
        RETURN c.name AS conferenceName,
               communityAuthors,
               editionCount AS editionsParticipated
        ORDER BY SIZE(communityAuthors) DESC
        """
        return self.run_query(query, "Query N2: Finding conference communities (authors with ≥4 editions)")

    def journal_impact_factors(self):
        query = """
        MATCH (p:Paper)-[:PUBLISHED_IN]-(j:Journal)
        WHERE p.type = 'Journal'
        OPTIONAL MATCH (p)-[:CITES]->(p1:Paper) 
        WITH j,
             COUNT(DISTINCT p) AS papers,
             COUNT(p1) AS totalCitations
        WHERE papers > 0     
        RETURN j.name AS journal_name,
               totalCitations,
               ToFloat(totalCitations)/papers AS impactFactor
        ORDER BY impactFactor DESC
        """
        return self.run_query(query, "Query N3: Calculating journal impact factors")

    def author_h_index(self):
        query = """
        MATCH (p1:Paper)<-[:CITES]-(p:Paper)-[:WRITTEN_BY]->(a:Author) 
        WITH a, p, count(p1) AS citations
        WITH a, p, citations
        WITH a, count(p) AS total, collect(citations) AS paperCitations
        WITH a, total, paperCitations, 
             [x in range(1, size(paperCitations)) WHERE x <= paperCitations[x - 1] | [paperCitations[x - 1], x] ] AS hindex
        WITH *, hindex[-1][1] AS hIndex
        RETURN a.name AS Author, hIndex
        ORDER BY hIndex DESC
        """
        return self.run_query(query, "Query N4: Calculating author h-index")

    def execute_and_display_queries(self):
        print("\n=== Starting Query Execution ===\n")
        
        queries = [
            ("1. Top-Cited Papers", self.top_cited_papers),
            ("2. Conference Communities", self.conference_communities),
            ("3. Journal Impact Factors", self.journal_impact_factors),
            ("4. Author H-Index", self.author_h_index)
        ]
        
        results = {}
        
        for name, query_func in queries:
            print(f" {name}...")
            query_results = query_func()
            results[name] = query_results
            
            print(f"\n Results for {name}:")
            if query_results:
                for i, record in enumerate(query_results, 1):
                    print(f"  {i}. {dict(record)}")
            else:
                print(" No results returned")
            print("-" * 60)
        
        print("\n=== All queries completed ===")
        return results

def main():
    neo4j = Neo4jQueries(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    try:
        neo4j.execute_and_display_queries()
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        neo4j.close()

if __name__ == "__main__":
    main()