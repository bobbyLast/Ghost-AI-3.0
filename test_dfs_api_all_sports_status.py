import os
from dotenv import load_dotenv
import requests

# Load API key from .env
load_dotenv()
API_KEY = os.getenv('ODDS_API_KEY')

SPORTS_URL = 'https://api.the-odds-api.com/v4/sports/'

print("Fetching all available sports and their status...")
try:
    response = requests.get(SPORTS_URL, params={'apiKey': API_KEY})
    response.raise_for_status()
    sports_list = response.json()
    for sport in sports_list:
        print(f"Key: {sport.get('key')}, Title: {sport.get('title')}, Active: {sport.get('active')}, Group: {sport.get('group')}, Details: {sport.get('details')}")
except Exception as e:
    print(f"❌ Failed to fetch sports list: {e}") 