# Waste Management Scraper

## Overview

The Waste Management Scraper is a Python-based tool designed to scrape LinkedIn posts related to waste management requirements. It utilizes the SERP API to fetch relevant posts and extracts information such as the poster's name, designation, company, and the content of the posts. The scraper also classifies the posts into predefined waste categories using vector embeddings and cosine similarity.

## Features

- Scrapes LinkedIn posts based on specified search queries.
- Extracts poster information including name, designation, and company.
- Classifies posts into waste categories using machine learning.
- Saves the scraped data in both JSON and CSV formats.
- Handles OAuth 2.0 authentication to access LinkedIn API.


## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd Market_assignment
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:

   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Scraping LinkedIn Posts

1. Open the `script.py` file and set your SERP API key in the `main()` function.
2. Run the script:

   ```bash
   python script.py
   ```

3. The scraped data will be saved in the `waste_management_data` directory in both JSON and CSV formats.

### OAuth 2.0 Authentication

1. Start the server to capture the authorization code:

   ```bash
   python server.py
   ```

2. Open your browser and navigate to the LinkedIn OAuth authorization URL. After authorizing, you will be redirected to the callback URL, and the authorization code will be printed in the terminal.

3. Use the `access_token.py` script to exchange the authorization code for an access token:

   ```bash
   python access_token.py
   ```

### Processing CSV Data

1. Use the `populate_csv.py` script to enrich the scraped data with additional LinkedIn post details:

   ```bash
   python populate_csv.py
   ```

## Code Explanation

### WasteManagementScraper Class

- **Initialization**: The class is initialized with a SERP API key and sets up search queries and waste categories.
- **Scraping Logic**: The `scrape_waste_management_requirements` method orchestrates the scraping process, fetching posts and extracting relevant information.
- **Poster Information**: The `search_poster_info` method retrieves the poster's designation and company using the SERP API.
- **Classification**: The `classify_waste_category` method uses vector embeddings to classify the content into waste categories.

### Server for OAuth 2.0

- **server.py**: A simple HTTP server that listens for incoming requests to capture the authorization code from LinkedIn's OAuth flow.

### Access Token Retrieval

- **access_token.py**: This script exchanges the authorization code for an access token, which is required to make authenticated requests to the LinkedIn API.

### CSV Data Processing

- **populate_csv.py**: This script processes the CSV file containing scraped LinkedIn posts, extracts additional details using the LinkedIn API, and saves the enriched data back to a CSV file.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [SERP API](https://serpapi.com/) for providing the search API.
- [Sentence Transformers](https://www.sbert.net/) for the embedding model used in classification.
- [LinkedIn API](https://docs.microsoft.com/en-us/linkedin/) for accessing LinkedIn data.

