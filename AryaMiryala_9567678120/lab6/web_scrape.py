import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from normalize import normalize_api
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.support.ui import WebDriverWait

BASE_SEARCH_URL = "https://www.drillingedge.com/search"
BASE_URL = "https://www.drillingedge.com"

def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)
    return driver


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def search_well(driver, api):
    api = normalize_api(api)

    url = (
        f"https://www.drillingedge.com/search?type=wells"
        f"&operator_name=&well_name=&api_no={api}"
        f"&lease_key=&state=&county=&section=&township=&range="
        f"&min_boe=&max_boe=&min_depth=&max_depth=&field_formation="
    )

    driver.get(url)

    wait = WebDriverWait(driver, 10)

    # wait for results table- seen w/ inspect element
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "table.interest_table tbody tr")
        )
    )

    # grab the link inside the table
    links = driver.find_elements(
        By.CSS_SELECTOR,
        "table.interest_table tbody tr td a"
    )

    if links:
        return links[0].get_attribute("href")

    return None

def scrape_well_page(driver, url):
    driver.get(url)
    time.sleep(2)

    html = driver.page_source
    data = {}

    #well name
    try:
        title_text = driver.find_element(By.TAG_NAME, "h1").text.strip()
        clean_name = re.sub(r'\|\s*API.*', '', title_text).strip()
        data["well_name"] = clean_name
    except:
        data["well_name"] = None

    rows = driver.find_elements(By.CSS_SELECTOR, "table.skinny tr")

    for row in rows:
        headers = row.find_elements(By.TAG_NAME, "th")
        cells = row.find_elements(By.TAG_NAME, "td")

        # Match each header with corresponding cell
        for i in range(min(len(headers), len(cells))):
            label = headers[i].text.strip()
            value = cells[i].text.strip()

            if label == "Well Status":
                data["well_status"] = value

            elif label == "Well Type":
                data["well_type"] = value

            elif label == "Closest City":
                data["closest_city"] = value

            elif label == "Latitude / Longitude":
                coords = value.split(",")
                if len(coords) == 2:
                    try:
                        data["latitude"] = float(coords[0].strip())
                        data["longitude"] = float(coords[1].strip())
                    except:
                        pass
    return data


def get_well_data(api):
    driver = create_driver()
    try:
        well_url = search_well(driver, api)
        if not well_url:
            print("No well found")
            return None

        print("Scraping:", well_url)
        data = scrape_well_page(driver, well_url)
        return data

    finally:
        driver.quit()


if __name__ == "__main__":
    #replace with json list
    test_api = "33-053-02102"
    data = get_well_data(test_api)
    print(data)