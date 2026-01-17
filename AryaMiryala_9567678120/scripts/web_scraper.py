import requests
from bs4 import BeautifulSoup
import os

#target url for the scraping task
url = "https://www.cnbc.com/world/?region=world"

headers = {
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

}

#send the get request to the url using headers
response = requests.get(url, headers=headers)

#make sure request was successful
if response.status_code == 200:
	#parse the html content
	soup = BeautifulSoup(response.content, 'html.parser')
	#define the file path
	file_path = os.path.join("..", "data", "raw_data", "web_data.html")
	
	#open the file for writing
	with open(file_path, "w", encoding = "utf-8") as f: 
		f.write(str(soup))

	print(f"Successfully saved data to {file_path}")
else: 
	print(f"Failed to retrieve data. Status code: {response.status_code}") 
