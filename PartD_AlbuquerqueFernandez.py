from neo4j import GraphDatabase

uri = "bolt://localhost:7689"
username = "lucia"
password = "lucia1234" 

def connect_to_neo4j():
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        print("Successfully connected to Neo4j")
        return driver
    except Exception as e:
        print(f"Connection failed: {e}")
        return None

def safe_drop_graph(session, graph_name):
    try:
        result = session.run(f"""
            CALL gds.graph.drop('{graph_name}', false)
            YIELD graphName
        """)
        if result.peek():
            print(f"Successfully dropped graph: {graph_name}")
        return True
    except Exception as e:
        if "Graph with name" in str(e) and "does not exist" in str(e):
            print(f"Graph {graph_name} didn't exist - nothing to drop")
            return True
        print(f"Error dropping graph {graph_name}: {str(e)[:200]}")
        return False

def create_graph_projection(session, graph_name, node_labels, relationship_config):
    max_retries = 2
    for attempt in range(max_retries):
        try:
            query = f"""
            CALL gds.graph.project(
                '{graph_name}',
                {node_labels},
                {relationship_config}
            )
            YIELD graphName, nodeCount, relationshipCount
            RETURN graphName, nodeCount, relationshipCount
            """
            result = session.run(query)
            stats = result.single()
            print(f"Successfully created {graph_name} with:")
            print(f"  - Nodes: {stats['nodeCount']}")
            print(f"  - Relationships: {stats['relationshipCount']}")
            return True
        except Exception as e:
            if "already exists" in str(e) and attempt == 0:
                print(f"Graph {graph_name} exists - attempting to drop and recreate...")
                if not safe_drop_graph(session, graph_name):
                    return False
                continue
            print(f"Failed to create {graph_name}: {str(e)[:200]}")
            return False
    return False

def analyze_similarity(session):
    print("\nRunning similarity analysis...")
    try:
        result = session.run("""
            CALL gds.nodeSimilarity.stream('similarity_graph', {
                topK: 3,
                similarityCutoff: 0.1
            })
            YIELD node1, node2, similarity
            RETURN 
                gds.util.asNode(node1).title AS paper1,
                gds.util.asNode(node2).title AS paper2,
                similarity
            ORDER BY similarity DESC
            LIMIT 10
        """)
        
        print("\nTOP SIMILAR PAPERS:")
        for i, record in enumerate(result, 1):
            print(f"{i}. {record['paper1'][:60]}")
            print(f"   Similar to: {record['paper2'][:60]}")
            print(f"   Similarity score: {record['similarity']:.3f}\n")
        return True
    except Exception as e:
        print(f"Similarity analysis failed: {e}")
        return False

def analyze_importance(session):
    print("\nRunning importance analysis...")
    try:
        # Verify graph exists first
        exists = session.run("""
            CALL gds.graph.exists('importance_graph') 
            YIELD exists
            RETURN exists
        """).single()["exists"]
        
        if not exists:
            print("Importance graph missing - attempting to create...")
            if not create_graph_projection(
                session,
                "importance_graph",
                "'Paper'",
                "{ CITES: { orientation: 'REVERSE' } }"
            ):
                return False

        result = session.run("""
            CALL gds.betweenness.stream('importance_graph')
            YIELD nodeId, score
            RETURN 
                gds.util.asNode(nodeId).title AS paper,
                score
            ORDER BY score DESC
            LIMIT 10
        """)
        
        print("\nMOST IMPORTANT PAPERS:")
        for i, record in enumerate(result, 1):
            print(f"{i}. {record['paper'][:70]}")
            print(f"   Importance score: {record['score']:.3f}\n")
        return True
    except Exception as e:
        print(f"Importance analysis failed: {e}")
        return False

def main():
    print("\n=== ACADEMIC PAPER ANALYSIS ===")
    driver = connect_to_neo4j()
    if not driver:
        return
    
    try:
        with driver.session() as session:
            # Set up graph projections
            print("\nSetting up graph projections...")
            if not create_graph_projection(
                session,
                "similarity_graph",
                "['Paper', 'Keyword']",
                "{ HAS_KEYWORD: {} }"
            ):
                print("Failed to set up similarity graph")
                return
            
            if not create_graph_projection(
                session,
                "importance_graph",
                "'Paper'",
                "{ CITES: { orientation: 'REVERSE' } }"
            ):
                print("Failed to set up importance graph")
                return
            
            # Run analyses
            print("\nStarting analyses...")
            similarity_success = analyze_similarity(session)
            importance_success = analyze_importance(session)
            
            if similarity_success and importance_success:
                print("\nAll analyses completed successfully!")
            else:
                print("\nAnalysis completed with some errors")
                
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        driver.close()
        print("\nDisconnected from Neo4j")

if __name__ == "__main__":
    main()