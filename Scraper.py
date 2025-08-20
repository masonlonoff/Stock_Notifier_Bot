# Scraper.py
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def parse_html(html: str):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", {"id": "main-table"})  
    if not table:
        raise ValueError("Table not found on the page")

    data = []
    rows = table.find("tbody").find_all("tr")
    for row in rows:
        sym_td = row.find("td", {"class": "sym svelte-1ro3niy"})
        if not sym_td:
            continue
        a = sym_td.find("a")
        if not a:
            continue
        symbol = a.text.strip()
        if symbol:
            data.append([symbol])

    return data

def scrape_symbols(url: str):
    driver = get_driver()
    try:
        driver.get(url)
        time.sleep(3) 
        html = driver.page_source
        return parse_html(html)
    finally:
        driver.quit()

def main() -> pd.DataFrame:
    large_cap_url = "https://stockanalysis.com/list/large-cap-stocks/"
    mega_cap_url  = "https://stockanalysis.com/list/mega-cap-stocks/"

    large_cap_data = scrape_symbols(large_cap_url)
    mega_cap_data  = scrape_symbols(mega_cap_url)

    combined_data = mega_cap_data + large_cap_data
    df = pd.DataFrame(combined_data, columns=["Symbol"])
    return df

if __name__ == "__main__":
    print(main())
