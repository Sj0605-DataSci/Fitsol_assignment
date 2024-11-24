import os
import requests
import pandas as pd
from datetime import datetime
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import os

# Disable tokenizers parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

class WasteManagementScraper:
    def __init__(self, tavily_api_key, output_dir="waste_management_data"):
        """Initialize the Waste Management Scraper with Tavily API and GPT-2 model."""
        self.tavily_api_key = tavily_api_key
        self.output_dir = output_dir
        self.headers = {'Authorization': f'Bearer {self.tavily_api_key}'}

        # Waste categories mapping as per document
        self.waste_categories = {
            'A': 'Plastic Waste',
            'B': 'E-waste',
            'C': 'Bio-medical Waste',
            'D': 'Construction and Demolition Waste',
            'E': 'Battery Waste',
            'F': 'Radioactive Waste',
            'G': 'Other Hazardous Waste',
            'H': 'Other Non-Hazardous Waste'
        }

        # Load GPT-2 model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained("gpt2")
        self.model = AutoModelForCausalLM.from_pretrained("gpt2")

        # Set device - force CPU usage to avoid MPS issues
        self.device = torch.device("cpu")
        self.model = self.model.to(self.device)

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

    def _generate_text(self, prompt, max_tokens=50):
        """Helper function to generate text while handling device placement."""
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=400)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                pad_token_id=self.tokenizer.eos_token_id,
                num_return_sequences=1,
                temperature=0.7
            )
            
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        except Exception as e:
            print(f"Error in text generation: {e}")
            return prompt  # Return original prompt if generation fails

    def rephrase_query(self, query):
        """Use GPT-2 model to rephrase the query for better supply/demand focus."""
        # Keep the prompt shorter to avoid Tavily's 400-char limit
        short_prompt = f"Rephrase the query about supply or demand in waste management {query}"
        return short_prompt

    def classify_requirement_type(self, content):
        """Classify if the post is a supply or demand requirement using keywords."""
        content = content.lower()
        supply_keywords = ['offering', 'available', 'providing', 'supply', 'service provider']
        demand_keywords = ['needed', 'seeking', 'looking for', 'required', 'wanted']
        
        supply_count = sum(1 for keyword in supply_keywords if keyword in content)
        demand_count = sum(1 for keyword in demand_keywords if keyword in content)
        
        return 'supply' if supply_count > demand_count else 'demand'

    def classify_waste_category(self, content):
        """Classify the waste category using keywords instead of ML."""
        content = content.lower()
        
        category_keywords = {
            'A': ['plastic', 'polymer', 'pet', 'packaging material'],
            'B': ['electronic', 'e-waste', 'computer', 'phone'],
            'C': ['medical', 'hospital', 'clinical', 'biomedical'],
            'D': ['construction', 'demolition', 'building', 'debris'],
            'E': ['battery', 'batteries', 'ups', 'cell'],
            'F': ['radioactive', 'nuclear', 'radiation'],
            'G': ['chemical', 'pesticide', 'herbicide', 'asbestos', 'sludge'],
            'H': ['food waste', 'paper', 'cardboard', 'textile', 'glass', 'wood']
        }
        
        # Count matches for each category
        matches = {cat: sum(1 for keyword in keywords if keyword in content)
                  for cat, keywords in category_keywords.items()}
        
        # Return category with most matches, or 'H' if no matches
        return max(matches.items(), key=lambda x: x[1])[0] if any(matches.values()) else 'H'

    def extract_poster_info(self, content):
        """Extract poster information using regex patterns and rules."""
        # Return empty defaults since we can't reliably extract this info
        return {
            "name": "",
            "designation": "",
            "company": ""
        }

    def fetch_posts(self, search_term):
        """Fetch posts from LinkedIn using Tavily Search API."""
        rephrased_query = self.rephrase_query(search_term)
        params = {
            'query': rephrased_query,
            'include_domains': ['linkedin.com/posts'],
            'max_results': 10,
            'search_depth': 'advanced'
        }
        
        try:
            response = requests.post(
                'https://api.tavily.com/search',
                headers=self.headers,
                json=params,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get('results', [])
            else:
                print(f"Error fetching results: {response.text}")
                return []
        except Exception as e:
            print(f"Exception in fetch_posts: {e}")
            return []

    def save_data(self, data):
        """Save scraped data to CSV with timestamp."""
        if not data:
            print("No data to save")
            return
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'waste_management_data_{timestamp}.csv'
        
        df = pd.DataFrame(data)
        output_path = os.path.join(self.output_dir, filename)
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"Data saved to {output_path}")

    def scrape_waste_management_requirements(self):
        """Main function to scrape waste management requirements."""
        # Shorter, more focused search terms
        search_terms = [
            "waste disposal",
            "recycling service",
            "hazardous waste",
            "waste management"
        ]
        
        all_results = []
        for search_term in search_terms:
            print(f"Searching for: {search_term}")
            try:
                posts = self.fetch_posts(search_term)
                
                for post in posts:
                    try:
                        content = post.get('content', '')
                        if not content:
                            continue
                            
                        result = {
                            'post_content': content,
                            'post_url': post.get('url', ''),
                            'requirement_type': self.classify_requirement_type(content),
                            'waste_category': self.classify_waste_category(content),
                            'waste_category_name': self.waste_categories.get(
                                self.classify_waste_category(content), 'Unknown'
                            )
                        }
                        
                        # Add poster info
                        poster_info = self.extract_poster_info(content)
                        result.update({
                            'poster_name': poster_info['name'],
                            'poster_designation': poster_info['designation'],
                            'poster_company': poster_info['company']
                        })
                        
                        all_results.append(result)
                    except Exception as e:
                        print(f"Error processing post: {e}")
                        continue
                        
            except Exception as e:
                print(f"Error processing search term {search_term}: {e}")
                continue
        
        self.save_data(all_results)
        return all_results

# Example usage
if __name__ == "__main__":
    scraper = WasteManagementScraper(tavily_api_key='travily API key')
    scraper.scrape_waste_management_requirements()
