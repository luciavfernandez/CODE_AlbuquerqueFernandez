from neo4j import GraphDatabase
import json

NEO4J_URI = "bolt://localhost:7689"  
NEO4J_USER = "lucia"
NEO4J_PASSWORD = "lucia1234"  


class Neo4jQueries:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def run_query(self, query, description, **kwargs):
        with self.driver.session() as session:
            print(f"\nRunning  {description}")
            try:
                result = session.run(query, **kwargs)
                return [record for record in result]
            except Exception as e:
                print(f"Error running : {e}")
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
        return self.run_query(query, "Query N1: Find the top 3 most cited papers of each conference/workshop:_")

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
        return self.run_query(query, "Query N2: For each conference/workshop find its community: i.e., those authors that have published papers on that conference or workshop in, at least, 4 different editions:_")

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
        return self.run_query(query, "Query N3: Find the impact factor of the journals in your graph:_")

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
        return self.run_query(query, "Query N4: Find the h-index of the authors in your graph: _")

    def execute_all_queries(self):
        results = {
            "N1_top_cited_papers": self.top_cited_papers(),
            "N2_conference_communities": self.conference_communities(),
            "N3_journal_impact_factors": self.journal_impact_factors(),
            "N4_author_h_index": self.author_h_index()
        }
        return results

def main():
    neo4j = Neo4jQueries(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    try:
        results = neo4j.execute_all_queries()
        
        # Print results in a structured way
        for query_name, records in results.items():
            print(f"\n=== Results for {query_name} ===")
            if records:
                for record in records:
                    print(dict(record))
            else:
                print("No results returned")
                
    finally:
        neo4j.close()

if __name__ == "__main__":
    main()