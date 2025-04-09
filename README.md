# CODE_AlbuquerqueFernandez

The main goal for this practice is to deep dive in the use of graph database, specifically Neo4j. A Neo4j graph database stores data as nodes, relationships, and properties instead of in tables or documents. This means one can organize data in a similar way as when sketching ideas on a whiteboard with balloons and arrows.

## Installation

Take into consideration the following installations:

1. Neo4j Desktop installed and running
2. An active database previously set and running in Neo4j Desktop (verify the default DB is called "neo4j") -> If not, change the proper python files (where there is needed a session in neo4j)
3. Plugin "Graph Data Science Library plugin" installed in the host machine or in the DBMS, the later can be done in the UI from Neo4j Desktop at a right side window on the Plugins tab when one selects the DBMS of a given project
4. The default port "bolt://localhost:7687" -> If not, change the proper python files (where there is needed a session in neo4j)
5. The default user "neo4j" and password "neo4j" -> If not, change the proper python files (where there is needed a session in neo4j)



## Implementation
For this solution, we will be using the Terminal, open it in the directory of the project. The first step is to create a virtual environment, we did with python3, but one can choose to do it with conda or other environment managers, we chose this to avoid any possible versioning conflicts and keep a clean environment for our application. So we expect python to be installed and available in the terminal with either python3 or python commands. Now, you should go to the Directory where your files are located. You will need to install two libraries in the new environment as well, the respective code follows:

 ```
   python3 -m venv myenv
   source myenv/bin/activate
   pip install neo4j
   pip install requests
```

Finally, run the following commands to see the available files from the project and run each of python files in the given order, replace the square brackets with the proper name of the files.

 ```
   ls
   python [file_name].py
 ```

## Source Codes

__synthetic_data.py__

This file contains synthetic data generation for a Neo4j database. It includes lists of keywords, conferences, journals, workshops, paper reviews, and affiliations. Everything related to Synthetic data is here. This file is used on the PartA.1_AlbuquerqueFernandez.py to enrich the data downloaded via de API.

__PartA.1_AlbuquerqueFernandez.png__

A schema representing the relationships between nodes like Author, Keyword, Paper, Edition, Volume, and Journal, along with their relationships (e.g., WRITTEN_BY, HAS_KEYWORD, PUBLISHED_IN).

__PartA.1_AlbuquerqueFernandez.py__

This script fetches Computer Science papers from the DBLP API, processes them, and enhances them with synthetic data (PartA.0_AlbuquerqueFernandez.py). The output is saved as dblp.json.

__PartA.2_AlbuquerqueFernandez.py__

This script loads the processed data from dblp.json into a Neo4j database. It creates nodes for papers, authors, keywords, and events (conferences, journals, workshops), and establishes relationships between them.

__PartA.3A_AlbuquerqueFernandez.png__

Updated diagram showing additional nodes like Review and Affiliation, and relationships like REVIEWED_BY, AFFILIATED_WITH, and CITES.

__PartA.3A_AlbuquerqueFernandez.py__

This script extends the Neo4j database by adding review nodes and author-affiliation relationships. It processes the dblp.json file to create these additional nodes and links.

__PartB_AlbuquerqueFernandez.py__

This file contains Neo4j queries to analyze the database. It includes 4 queries to find:

 1. Top-cited papers
 2. Conference communities
 3. Journal impact factors
 4. Authors' h-index.

__PartC_AlbuquerqueFernandez.py__

This script defines and executes advanced Neo4j queries to identify a "Database Community" based on keywords (Data Management, Indexing, Data Modeling, Big
Data, Data Processing, Data Storage and Data Querying), find top papers in this community, and identify potential reviewers and "gurus".

__PartD_AlbuquerqueFernandez.py__

This script performs graph analysis using Neo4j's Graph Data Science (GDS) library. It sets up graph projections for similarity and importance analysis, then runs algorithms to find similar papers and identify the most influential papers based on betweenness centrality.

Finally, you can deactivate the python environment used to run the project, if you used a dedicated one.

 ```
   deactivate
 ```
