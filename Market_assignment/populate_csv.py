import requests
import pandas as pd
from urllib.parse import urlparse
import re
import time
from requests.exceptions import RequestException

class LinkedInPostAnalyzer:
    def __init__(self, access_token):
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        self.rate_limit_delay = 1  # Delay between requests in seconds

    def extract_activity_id(self, post_url):
        try:
            parsed_url = urlparse(post_url)
            path_segments = parsed_url.path.split('/')
            for segment in path_segments:
                if 'activity' in segment:
                    # Extract the numeric activity ID
                    activity_id = re.search(r'activity-(\d+)', segment)
                    if activity_id:
                        return activity_id.group(1)
            return None
        except Exception as e:
            print(f"Error extracting activity ID: {str(e)}")
            return None

    def make_api_request(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            time.sleep(self.rate_limit_delay)  # Rate limiting
            return response.json()
        except RequestException as e:
            print(f"API request failed: {str(e)}")
            return None

    def fetch_post_details(self, activity_id):
        url = f'https://api.linkedin.com/v2/activities/{activity_id}'
        return self.make_api_request(url)

    def fetch_author_details(self, author_urn):
        url = f'https://api.linkedin.com/v2/people/(id:{author_urn})'
        return self.make_api_request(url)

    def process_posts(self, input_file, output_file):
        try:
            df = pd.read_csv(input_file)
            
            for index, row in df.iterrows():
                try:
                    post_url = row['Post_URL']
                    activity_id = self.extract_activity_id(post_url)
                    
                    if not activity_id:
                        print(f"Invalid post URL or missing activity ID: {post_url}")
                        continue

                    post_details = self.fetch_post_details(activity_id)
                    if not post_details:
                        continue

                    author_urn = post_details.get('actor')
                    created_time = post_details.get('created', {}).get('time')

                    if author_urn:
                        author_id = author_urn.split(':')[-1]
                        author_details = self.fetch_author_details(author_id)
                        
                        if author_details:
                            df.at[index, 'Poster_Name'] = (
                                f"{author_details.get('localizedFirstName', '')} "
                                f"{author_details.get('localizedLastName', '')}".strip()
                            )
                            df.at[index, 'Poster_Designation'] = author_details.get('headline', '')
                            df.at[index, 'Poster_Company'] = (
                                author_details.get('positions', {})
                                .get('values', [{}])[0]
                                .get('company', {})
                                .get('name', '')
                            )
                            if created_time:
                                df.at[index, 'Post_Date'] = pd.to_datetime(created_time, unit='ms')

                except Exception as e:
                    print(f"Error processing row {index}: {str(e)}")
                    continue

            df.to_csv(output_file, index=False)
            print(f"Successfully processed data and saved to {output_file}")
            
        except Exception as e:
            print(f"Failed to process file: {str(e)}")

def main():
    ACCESS_TOKEN = 'AQV1bEP_5ngQXdQhKjqVFeSalSMxYZ9ORaz8eNFV41Xi7Dtw-t6VDBuf3B2ZPtl3uKDlv3MDgFfvuCJEvJ6StT1NwUWceU6sjIpAMTtuLpidVzz4oaN5vwNsdDYm9fm8EmO_yKU0OyeSlExs2-Z-RL9Y-tJWB2CV1en_2ij9I672KWsZwpmn2lGU8NIlEIxAvDeEunhGdHjv6d1EC4XLLWboNeTBRDF1J1_rVoRi6pE6tNr_SZXlBaAwXhbebmL8LPgI7omWEdC4M5deYi80UIwxH8UcCLwP2lxgfqJDcSQmr7BoxjNbkQUN7nRn19YFVtI6kxx4vMD72wxYjjgywv4UpSOZVg'
    analyzer = LinkedInPostAnalyzer(ACCESS_TOKEN)
    analyzer.process_posts('/Users/sammy/Desktop/Fitsol/Market_assignment/updated_waste_management_data_20241123_234349.csv', '/Users/sammy/Desktop/Fitsol/Market_assignment/updated_waste_management_data_20241123_234349.csv')

if __name__ == "__main__":
    main()