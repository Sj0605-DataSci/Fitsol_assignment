import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import datetime, timedelta
import time
import re
from sentence_transformers import SentenceTransformer, util

class WasteManagementScraper:
    def __init__(self, serp_api_key):
        """Initialize the scraper with SERP API key"""
        self.api_key = serp_api_key
        self.base_url = "https://serpapi.com/search.json"
        
        self.search_queries = [
            'site:linkedin.com/posts "waste management requirements" after:2024-01-01 before:2024-11-24',
            'site:linkedin.com/posts "waste disposal needed" after:2024-01-01 before:2024-11-24',
            'site:linkedin.com/posts #PlasticWaste after:2024-01-01 before:2024-11-24',
            'site:linkedin.com/posts #EwasteManagement after:2024-01-01 before:2024-11-24',
            'site:linkedin.com/posts #SustainableWaste after:2024-01-01 before:2024-11-24',
            'site:linkedin.com/posts "recycling requirements" after:2024-01-01 before:2024-11-24',
            'site:linkedin.com/posts "hazardous waste disposal" after:2024-01-01 before:2024-11-24'
        ]
        
        self.waste_categories = {
            'A': {
                'name': 'Plastic Waste',
                'keywords': ['plastic', 'PET', 'polymer', 'packaging waste']
            },
            'B': {
                'name': 'E-waste',
                'keywords': ['electronic', 'e-waste', 'computer', 'electronics']
            },
            'C': {
                'name': 'Bio-medical Waste',
                'keywords': ['medical', 'hospital', 'clinical', 'biomedical', 'healthcare waste']
            },
            'D': {
                'name': 'Construction and Demolition Waste',
                'keywords': ['construction', 'demolition', 'building waste']
            },
            'E': {
                'name': 'Battery Waste',
                'keywords': ['battery', 'batteries', 'UPS']
            },
            'F': {
                'name': 'Radioactive Waste',
                'keywords': ['radioactive', 'nuclear', 'radiation']
            },
            'G': {
                'name': 'Other Hazardous Waste',
                'subcategories': {
                    'G1': {'name': 'Chemical Waste', 'keywords': ['chemical', 'paint', 'solvent']},
                    'G2': {'name': 'Pesticides and Herbicides', 'keywords': ['pesticide', 'herbicide', 'agricultural chemical']},
                    'G3': {'name': 'Asbestos', 'keywords': ['asbestos']},
                    'G4': {'name': 'Industrial Sludge', 'keywords': ['sludge', 'industrial waste']},
                    'G5': {'name': 'Contaminated Soil', 'keywords': ['contaminated soil', 'polluted soil']}
                }
            },
            'H': {
                'name': 'Other Non-Hazardous Waste',
                'subcategories': {
                    'H1': {'name': 'Food Waste', 'keywords': ['food waste', 'organic waste']},
                    'H2': {'name': 'Paper and Cardboard', 'keywords': ['paper', 'cardboard']},
                    'H3': {'name': 'Textile Waste', 'keywords': ['textile', 'fabric', 'clothes']},
                    'H4': {'name': 'Glass Waste', 'keywords': ['glass']},
                    'H5': {'name': 'Wood Waste', 'keywords': ['wood', 'sawdust', 'pallets']},
                    'H6': {'name': 'Rubber Waste', 'keywords': ['rubber', 'tire']}
                }
            }
        }

        print("Loading the sentence transformer model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Model loaded successfully.")
        self.category_embeddings = self.create_category_embeddings()

    def create_category_embeddings(self):
        category_names = [data['name'] for data in self.waste_categories.values()]
        print("Creating category embeddings...")
        embeddings = self.model.encode(category_names, convert_to_tensor=True)
        print("Category embeddings created successfully.")
        return embeddings

    def fetch_linkedin_posts(self, query, num_results=100):
        try:
            print(f"Fetching posts for query: {query}")
            params = {
                "engine": "google",
                "q": query,
                "api_key": self.api_key,
                "num": num_results,
                "gl": "us",
                "filter": "0"
            }
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching results for query '{query}': {str(e)}")
            return None

    def extract_post_urls(self, search_results):
        post_urls = []
        if not search_results or 'organic_results' not in search_results:
            return post_urls
            
        for result in search_results['organic_results']:
            link = result.get('link', '')
            if 'linkedin.com/posts' in link or 'linkedin.com/feed/update' in link:
                post_urls.append({
                    'url': link,
                    'snippet': result.get('snippet', ''),
                    'title': result.get('title', ''),
                    'poster_name': self.extract_poster_name(result.get('title', ''))
                })
        return post_urls

    def extract_poster_name(self, title):
        """Extract the poster's name from the title."""
        # Assuming the title format is "Name - Title | Company"
        return title.split(' - ')[0] if ' - ' in title else title.split(' | ')[0]

    def search_poster_info(self, poster_name):
        """Search for the poster's designation and company using SERP API."""
        query = f"{poster_name} LinkedIn"
        params = {
            "engine": "google",
            "q": query,
            "api_key": self.api_key,
            "num": 1,
            "gl": "us",
            "filter": "0"
        }
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        return response.json()

    def extract_designation_company(self, search_results):
        """Extract designation and company from the search results."""
        if not search_results or 'organic_results' not in search_results:
            return '', ''
        
        for result in search_results['organic_results']:
            title = result.get('title', '')
            if ' at ' in title:
                parts = title.split(' at ')
                designation = parts[0].strip()
                company = parts[1].strip() if len(parts) > 1 else ''
                return designation, company
        return '', ''

    def classify_waste_category(self, text):
        print(f"Classifying waste category for text: {text}")
        text_embedding = self.model.encode(text, convert_to_tensor=True)
        cosine_scores = util.pytorch_cos_sim(text_embedding, self.category_embeddings)[0]
        top_category_idx = cosine_scores.argmax().item()
        top_category = list(self.waste_categories.keys())[top_category_idx]
        print(f"Top category identified: {top_category}-{self.waste_categories[top_category]['name']}")
        return f"{top_category}-{self.waste_categories[top_category]['name']}"

    def extract_requirement_info(self, post_data):
        content = post_data.get('snippet', '')
        title = post_data.get('title', '')
        poster_name = post_data.get('poster_name', '')

        # Search for poster's designation and company
        search_results = self.search_poster_info(poster_name)
        designation, company = self.extract_designation_company(search_results)

        return {
            'Post_Content': content,
            'Requirement_Category': self.classify_waste_category(content + ' ' + title),
            'Poster_Name': poster_name,
            'Poster_Designation': designation,
            'Poster_Company': company,
            'Post_URL': post_data.get('url', ''),
            'Collection_Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def save_results(self, results, filename_prefix='waste_management_data'):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_filename = f"{filename_prefix}_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        csv_filename = f"{filename_prefix}_{timestamp}.csv"
        df = pd.DataFrame(results)
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        
        print(f"\nData saved to:")
        print(f"- JSON: {json_filename}")
        print(f"- CSV: {csv_filename}")

    def scrape_waste_management_requirements(self):
        all_results = []
        print("Starting LinkedIn waste management requirements scraping...")
        
        for query in self.search_queries:
            print(f"\nProcessing query: {query}")
            search_results = self.fetch_linkedin_posts(query)
            if not search_results:
                continue
                
            post_data_list = self.extract_post_urls(search_results)
            for post_data in post_data_list:
                requirement_info = self.extract_requirement_info(post_data)
                all_results.append(requirement_info)
                
            time.sleep(2)
        
        unique_results = {result['Post_URL']: result for result in all_results}.values()
        unique_results = list(unique_results)
        self.save_results(unique_results)
        
        print(f"\nScraping completed!")
        print(f"Total posts collected: {len(unique_results)}")
        
        category_counts = {}
        for result in unique_results:
            categories = result['Requirement_Category'].split(', ')
            for category in categories:
                category_counts[category] = category_counts.get(category, 0) + 1
        
        print("\nCategory distribution:")
        for category, count in category_counts.items():
            print(f"{category}: {count} posts")
        
        return unique_results



def main():
    # Initialize scraper
    SERP_API_KEY = "your-api-key"
    scraper = WasteManagementScraper(SERP_API_KEY)
    
    try:
        # Run scraper
        results = scraper.scrape_waste_management_requirements()
        
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        import traceback
        print("\nDetailed error:")
        print(traceback.format_exc())

if __name__ == "__main__":
    main()    