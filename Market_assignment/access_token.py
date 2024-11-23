import requests

# Replace with your actual values
client_id = '86gmfrfvq48ug5'
client_secret = 'WPL_AP1.ILhowBIBHvYAcNOZ.SviJug=='
redirect_uri = 'http://localhost:8000/callback'
authorization_code = 'AQSWfv_k1jcO67_jhlnG2j_O5inLG8XGWbTCsEmhCjq7KnZ9mlO0HOegnzeK1Sm9S6oQo64YcbgY6Pvd_zqL5NA9IEsBm_vcXFyufUYuPTMK-FtHF-CAMKfI8sKmxp6IojsJG5NO3jHBozBrNRaVOMyCixhG0sZVQ52Q2Lt8o2aR5PX3nHc77qqAJH5qzSc9SjYFZjvM747U20Cu-AM'

token_url = 'https://www.linkedin.com/oauth/v2/accessToken'

# Prepare the payload
payload = {
    'grant_type': 'authorization_code',
    'code': authorization_code,
    'redirect_uri': redirect_uri,
    'client_id': client_id,
    'client_secret': client_secret
}

# Make the POST request to obtain the access token
response = requests.post(token_url, data=payload)

if response.status_code == 200:
    tokens = response.json()
    access_token = tokens.get('access_token')
    print(f"Access Token: {access_token}")
else:
    print(f"Error: {response.json()}")
