# CODE_AlbuquerqueFernandez

The main goal for this practice is to deep dive in the use of graph database, specifically Neo4j. A Neo4j graph database stores data as nodes, relationships, and properties instead of in tables or documents. This means you can organize your data in a similar way as when sketching ideas on a whiteboard.

## Installation

Take into consideration the following installations:

1. Neo4j Desktop installed
2. Plugin "Graph Data Science Library plugin"
3. Database previously set (review the default DB is called "neo4j") -> If not, change the proper python files (where there is needed a session in neo4j)
4. The default port "bolt://localhost:7687" -> If not, change the proper python files (where there is needed a session in neo4j)
5. The default user "neo4j" and password "neo4j" -> If not, change the proper python files (where there is needed a session in neo4j)



## Implementation
For this solution, we will be using the Terminal.The first step is to create a virtual environment. For this, you should go to the Directory where your files are located.

Later, you need to create the virtual environment (if not created already), run the following commands to create a whole new one:

 ```
   python3 -m venv myenv
   source myenv/bin/activate
   pip install neo4j
   python [file_name].py
   ```

## Source Codes

PartA.0_AlbuquerqueFernandez.py:
This file contains synthetic data generation for a Neo4j database. It includes lists of keywords, conferences, journals, workshops, paper reviews, and affiliations.Everything related to Synthetic data is here. This file is used on the PartA.1_AlbuquerqueFernandez.py for the requesting data from the API.

PartA.1_AlbuquerqueFernandez.png:
An schema representing the relationships between nodes like Author, Keyword, Paper, Edition, Volume, and Journal, along with their relationships (e.g., WRITTEN_BY, HAS_KEYWORD, PUBLISHED_IN).

PartA.1_AlbuquerqueFernandez.py:
This script fetches Computer Science papers from the DBLP API, processes them, and enhances them with synthetic data (PartA.0_AlbuquerqueFernandez.py). The output is saved as dblp.json.

PartA.2_AlbuquerqueFernandez.py:
This script loads the processed data from dblp.json into a Neo4j database. It creates nodes for papers, authors, keywords, and events (conferences, journals, workshops), and establishes relationships between them.

PartA.3A_AlbuquerqueFernandez.png:
Updated diagram showing additional nodes like Review and Affiliation, and relationships like REVIEWED_BY, AFFILIATED_WITH, and CITES.

PartA.3A_AlbuquerqueFernandez.py:
This script extends the Neo4j database by adding review nodes and author-affiliation relationships. It processes the dblp.json file to create these additional nodes and links.

PartB_AlbuquerqueFernandez.py:
This file contains Neo4j queries to analyze the database. It includes 4 queries to find:

 1. top-cited papers
 2. conference communities journal impact factors
 3. authors' h-index.

PartC_AlbuquerqueFernandez.py:
This script defines and executes advanced Neo4j queries to identify a "Database Community" based on keywords (Data Management, Indexing, Data Modeling, Big
Data, Data Processing, Data Storage and Data Querying), find top papers in this community, and identify potential reviewers and "gurus".

PartD_AlbuquerqueFernandez.py:
This script performs graph analysis using Neo4j's Graph Data Science (GDS) library. It sets up graph projections for similarity and importance analysis, then runs algorithms to find similar papers and identify the most influential papers based on betweenness centrality.




