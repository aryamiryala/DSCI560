import requests
from bs4 import BeautifulSoup
import os

url = "https://www.cnbc.com/world/?region=world"

headers = {
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

}

response = requests.get(url, headers=headers)

if response.status_code == 200:
	soup = BeautifulSoup(response.content, 'html.parser')
	file_path = os.path.join("..", "data", "raw_data", "web_data.html")

	with open(file_path, "w", encoding = "utf-8") as f: 
		f.write(str(soup))

	print(f"Successfully saved data to {file_path}")
else: 
	print(f"Failed to retrieve data. Status code: {response.status_code}") 
