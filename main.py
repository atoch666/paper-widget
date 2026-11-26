import os
import random
import requests
import xml.etree.ElementTree as ET

NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def fetch_random_arxiv_paper():
    # Suche nach Papers aus dem Bereich Informatik/KI (cs.AI)
    url = "http://export.arxiv.org/api/query?search_query=cat:cs.AI&max_results=50&sortBy=submittedDate&sortOrder=descending"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Fehler beim Abrufen der arXiv-Daten: {response.status_code}")
        
    root = ET.fromstring(response.content)
    atom_ns = "{http://www.w3.org/2005/Atom}"
    
    entries = root.findall(f"{atom_ns}entry")
    if not entries:
        return None
        
    entry = random.choice(entries)
    title = entry.find(f"{atom_ns}title").text.strip().replace("\n", " ")
    link = entry.find(f"{atom_ns}id").text.strip()
    
    cover_url = "https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=1000&q=80"
    
    return {
        "title": title,
        "link": link,
        "cover": cover_url
    }

def add_to_notion(paper):
    if not paper:
        print("Kein Paper gefunden.")
        return

    if not NOTION_API_KEY or not DATABASE_ID:
        print("Fehler: NOTION_API_KEY oder NOTION_DATABASE_ID sind nicht gesetzt!")
        return

    data = {
        "parent": {"database_id": DATABASE_ID},
        "cover": {
            "type": "external",
            "external": {"url": paper["cover"]}
        },
        "properties": {
            # Hinweis: Diese Namen müssen exakt mit deinen Spaltennamen in Notion übereinstimmen
            "Name": {
                "title": [
                    {
                        "text": {"content": paper["title"]}
                    }
                ]
            },
            "Link": {
                "url": paper["link"]
            }
        }
    }

    response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=data)
    if response.status_code == 200:
        print("Paper erfolgreich zu Notion hinzugefügt!")
    else:
        print(f"Fehler bei Notion ({response.status_code}): {response.text}")

if __name__ == "__main__":
    paper = fetch_random_arxiv_paper()
    add_to_notion(paper)
