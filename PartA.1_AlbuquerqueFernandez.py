import requests
import json
import random
import uuid
import re
from synthetic_data import *

query = "Computer Science" 
hits = 1000 
response_format = "json" 

url = f"https://dblp.org/search/publ/api?q={query.replace(' ', '+')}&h={hits}&format={response_format}"


# Send a GET request to DBLP API
response = requests.get(url)



if response.status_code == 200:

    data = response.json()

  
    papers = data["result"]["hits"].get("hit", [])

    
    all_authors = set()
    author_dict = {}  

    for paper in papers:
        authors = paper["info"].get("authors", {}).get("author", [])
        
        # If only one author, wrap it in a list
        if isinstance(authors, dict):
            authors = [authors]

        for author in authors:
            author_id = author.get("@pid", "unknown_id")
            # Fix the author text decoding
            author_text = author.get("text", "")
            if isinstance(author_text, str):
                # Handle any escaped unicode characters properly
                try:
                    author_text = author_text.encode('utf-8').decode('unicode_escape')
                except:
                    pass  # if decoding fails, keep original text
            all_authors.add((author_id, author_text))
            author_dict[author_text] = {"@pid": author_id, "text": author_text}


    author_list = list(all_authors)
    
   
    paper_ids = [str(uuid.uuid4()) for _ in papers]
    
 
    for i, paper in enumerate(papers):
        info = paper["info"]
        
        
        paper_id = paper_ids[i]
  
        keywords = random.sample(keyword_list, 3)
        review = random.sample(paper_reviews, 1)
        affiliation = random.sample(affiliations, 1)
        

        authors = info.get("authors", {}).get("author", [])
        if isinstance(authors, dict):
            authors = [authors]
        

        current_authors = {author["text"] for author in authors}

        
        possible_reviewers = [author_dict[name] for name in author_dict if name not in current_authors]
        selected_reviewers = random.sample(possible_reviewers, 3) if len(possible_reviewers) >= 3 else possible_reviewers
        
        reviewers = selected_reviewers if len(selected_reviewers) > 1 else selected_reviewers[0] if selected_reviewers else {}
        
       
        cited_papers = []
        available_papers = [p for j, p in enumerate(papers) if paper_ids[j] != paper_id]
        
       
        random.shuffle(available_papers)
        for p in available_papers:
            cited_authors = p["info"].get("authors", {}).get("author", [])
            if isinstance(cited_authors, dict):
                cited_authors = [cited_authors]
            cited_author_names = {a["text"] for a in cited_authors}
            
           
            if not current_authors.intersection(cited_author_names):
                cited_papers.append(paper_ids[papers.index(p)])
                if len(cited_papers) >= min(random.randint(1, 5), len(available_papers)):
                    break

        new_info = {}
        for key, value in info.items():
            new_info[key] = value
            if key == "authors":  
                new_info["paperid"] = paper_id
        
        new_info["keywords"] = keywords
        new_info["reviewers"] = {"author": reviewers}
        new_info["review"] = review
        new_info["affiliation"] = affiliation
        new_info["cited"] = cited_papers
        new_info = update_type(new_info)
        new_info = assign_event_attributes(new_info)
        
        paper["info"] = new_info

    with open("dblp.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4)

    
    for i, paper in enumerate(papers, 1):
        print(f"\n--- Paper {i} ---")
        for key, value in paper["info"].items():
            print(f"{key}: {value}")

    print("\nUpdated data saved as dblp.json")

else:
    print("Failed to retrieve data from DBLP API")