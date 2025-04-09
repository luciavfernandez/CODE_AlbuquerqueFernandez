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
            print(f"\nRunning  {description}")
            try:
                result = session.run(query, **kwargs)
                return [record for record in result]
            except Exception as e:
                print(f"Error running : {e}")
                return None

    def n1_database_community(self):
        query = """
        MATCH (p:Paper)-[:HAS_KEYWORD]->(k:Keyword)
        WHERE k.name IN ['Data Management', 'Indexing', 'Data Modeling', 'Big Data', 'Data Processing', 'Data Storage', 'Data Querying'] 
        RETURN p.title AS Title, k.name AS Keyword
        """

        return self.run_query(query, "N1: Define database community keywords")

    def n2_paper_communities(self):
        query = """     
            MATCH (j:Journal)<-[:PUBLISHED_IN]-(p:Paper)-[:HAS_KEYWORD]->(k:Keyword)
            WHERE k.name IN ['Data Management', 'Indexing', 'Data Modeling', 'Big Data', 'Data Processing', 'Data Storage', 'Data Querying'] 
            WITH j, COUNT(p) AS total_papers
            MATCH (j)<-[:PUBLISHED_IN]-(p2:Paper)-[:HAS_KEYWORD]->(k2:Keyword)
            WHERE k2.name IN ['Data Management', 'Indexing', 'Data Modeling', 'Big Data', 'Data Processing', 'Data Storage', 'Data Querying'] 
            WITH j, p2, total_papers, COUNT(p2) AS matching_papers
            WHERE (1.0 * matching_papers / total_papers) >= 0.9
            RETURN p2.type AS PublicationType,
                   j.name AS EventName, 
                   matching_papers AS CommunityPaper
            ORDER BY CommunityPaper DESC         

            UNION
    
            MATCH (c:Conference)<-[:PUBLISHED_IN]-(p:Paper)-[:HAS_KEYWORD]->(k:Keyword)
            WHERE k.name IN ['Data Management', 'Indexing', 'Data Modeling', 'Big Data', 'Data Processing', 'Data Storage', 'Data Querying'] 
            WITH c, COUNT(p) AS total_papers
            MATCH (c)<-[:PUBLISHED_IN]-(p2:Paper)-[:HAS_KEYWORD]->(k2:Keyword)
            WHERE k2.name IN ['Data Management', 'Indexing', 'Data Modeling', 'Big Data', 'Data Processing', 'Data Storage', 'Data Querying'] 
            WITH c, p2, total_papers, COUNT(p2) AS matching_papers
            WHERE (1.0 * matching_papers / total_papers) >= 0.9
            RETURN  p2.type AS PublicationType,
                    c.name AS EventName, 
                   matching_papers AS CommunityPaper
            ORDER BY CommunityPaper DESC  

        """
        return self.run_query(query, "N2: Find papers for community")

    def n3_top_papers(self):
        query = """
        // 1. Create or clear the Community node
        MERGE (comm:Community {name: 'Database Community'})
        WITH comm
        OPTIONAL MATCH (comm)-[r:HAS_TOP_PAPER]->()
        DELETE r
        WITH comm

        // 2. Link community keywords
        MATCH (k:Keyword)
        WHERE k.name IN ['Data Management', 'Indexing', 'Data Modeling', 'Big Data', 'Data Processing', 'Data Storage', 'Data Querying']
        MERGE (k)-[:REPRESENTS]->(comm)
        WITH comm

        // 3. Identify database venues (journals/conferences with ≥90% DB papers)
        CALL () {
            // For journals
            MATCH (j:Journal)<-[:PUBLISHED_IN]-(p:Paper)-[:HAS_KEYWORD]->(k:Keyword)
            WHERE k.name IN ['Data Management', 'Indexing', 'Data Modeling', 'Big Data', 'Data Processing', 'Data Storage', 'Data Querying']
            WITH j, COUNT(p) AS db_papers
            MATCH (j)<-[:PUBLISHED_IN]-(p2:Paper)
            WITH j, db_papers, COUNT(p2) AS total_papers
            WHERE (1.0 * db_papers / total_papers) >= 0.9
            RETURN j AS venue
            
            UNION
            
            // For conferences
            MATCH (c:Conference)<-[:PUBLISHED_IN]-(p:Paper)-[:HAS_KEYWORD]->(k:Keyword)
            WHERE k.name IN ['Data Management', 'Indexing', 'Data Modeling', 'Big Data', 'Data Processing', 'Data Storage', 'Data Querying']
            WITH c, COUNT(p) AS db_papers
            MATCH (c)<-[:PUBLISHED_IN]-(p2:Paper)
            WITH c, db_papers, COUNT(p2) AS total_papers
            WHERE (1.0 * db_papers / total_papers) >= 0.9
            RETURN c AS venue
        }
        WITH COLLECT(venue) AS db_venues, comm

        // 4. Find and process papers from these venues
        UNWIND db_venues AS venue
        MATCH (venue)<-[:PUBLISHED_IN]-(paper:Paper)
        WITH comm, paper, db_venues
        MATCH (citedBy:Paper)-[:CITES]->(paper)
        WHERE EXISTS {
            MATCH (citedBy)-[:PUBLISHED_IN]->(v) 
            WHERE v IN db_venues
        }
        WITH 
            comm,
            paper,
            COUNT(citedBy) AS communityCitations
        ORDER BY communityCitations DESC
        LIMIT 100

        // 5. Connect top papers to community
        MERGE (comm)-[:HAS_TOP_PAPER {citations: communityCitations}]->(p:paper)

        // 6. Return results
        RETURN 
            comm.name AS Community,
            paper.title AS TopPaper,
            paper.type AS PublicationType,
            communityCitations 
        ORDER BY communityCitations DESC;
        """
        return self.run_query(query, "Step 3: Find top 100 papers in database (node) Community")

    def n4_reviewers_and_gurus(self):
        query = """
        MERGE (comm:Community {name: 'Database Community'})
        WITH comm
        OPTIONAL MATCH (comm)-[r:HAS_TOP_PAPER]->()
        DELETE r
        WITH comm

        CALL () {
            MATCH (j:Journal)<-[:PUBLISHED_IN]-(p:Paper)-[:HAS_KEYWORD]->(k:Keyword)
            WHERE k.name IN ['Data Management', 'Indexing', 'Data Modeling', 'Big Data', 'Data Processing', 'Data Storage', 'Data Querying']
            WITH j, COUNT(p) AS db_papers
            MATCH (j)<-[:PUBLISHED_IN]-(p2:Paper)
            WITH j, db_papers, COUNT(p2) AS total_papers
            WHERE (1.0 * db_papers / total_papers) >= 0.9
            RETURN j AS venue
            UNION
            MATCH (c:Conference)<-[:PUBLISHED_IN]-(p:Paper)-[:HAS_KEYWORD]->(k:Keyword)
            WHERE k.name IN ['Data Management', 'Indexing', 'Data Modeling', 'Big Data', 'Data Processing', 'Data Storage', 'Data Querying']
            WITH c, COUNT(p) AS db_papers
            MATCH (c)<-[:PUBLISHED_IN]-(p2:Paper)
            WITH c, db_papers, COUNT(p2) AS total_papers
            WHERE (1.0 * db_papers / total_papers) >= 0.9
            RETURN c AS venue
        }
        WITH COLLECT(venue) AS db_venues, comm
        WHERE size(db_venues) > 0  // Ensure we have venues

        // Find papers with any citations (not just from community)
        UNWIND db_venues AS venue
        MATCH (venue)<-[:PUBLISHED_IN]-(paper:Paper)
        WITH comm, paper, db_venues
        MATCH (citedBy:Paper)-[:CITES]->(paper)
        WITH 
            comm,
            paper,
            COUNT(citedBy) AS communityCitations
        ORDER BY communityCitations DESC
        LIMIT 100

        // Connect papers and authors
        MERGE (comm)-[:HAS_TOP_PAPER {citations: communityCitations}]->(paper)
        WITH comm, paper
        MATCH (paper)-[:WRITTEN_BY]->(author:Author)
        MERGE (author)-[:POTENTIAL_REVIEWER]->(comm)
        WITH author, COUNT(paper) AS top_paper_count
        WHERE top_paper_count > 1
        SET author:Guru
        RETURN author.name AS GuruName, top_paper_count AS TopPapersCount
        ORDER BY top_paper_count DESC
        """
        return self.run_query(query, "Step 4: Identify reviewers and gurus")

    def execute_and_display_queries(self):

        print("\n=== Starting Query Execution ===\n")
        
        queries = [
            ("1. Community Definition", self.n1_database_community),
            ("2. Venue Identification", self.n2_paper_communities),
            ("3. Community Database", self.n3_top_papers),
            ("4. Gurus Identification", self.n4_reviewers_and_gurus)
        ]
        
        results = {}
        
        for name, query_func in queries:
            print(f"[RUNNING] {name}...")
            try:
                query_results = query_func()
                results[name] = query_results
                
                print(f"\n Results for {name}:")
                if query_results:
                    for i, record in enumerate(query_results, 1):
                        print(f"  {i}. {dict(record)}")
                else:
                    print("  No results returned")
                print("-" * 60)
                
            except Exception as e:
                print(f" Error in {name}: {str(e)}")
                results[name] = None
        
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