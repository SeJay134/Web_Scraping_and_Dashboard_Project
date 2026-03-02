# 1. Web Scraping Program

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import logging
import re

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# setup
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Enable headless mode
options.add_argument('--disable-gpu')  # Optional, recommended for Windows
options.add_argument('--window-size=1920x1080')  # Optional, set window size
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) " "AppleWebKit/537.36 (KHTML, like Gecko) " "Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)

driver.get("https://www.baseball-almanac.com/yearmenu.shtml")

wait = WebDriverWait(driver, 5)

wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

# function for checking getting data from web
def logging_check(data, name):
    if not data:
        raise ValueError(f'{name} is empty')
    logging.info(f'{name} is ok')

# function for checking df
def counter_columns(df_data, name):
    count = df_data.shape[1]
    print(f'{name}: {count} "columns"')

title = driver.title
logging_check(title, "title")

banners = []
name_banner = driver.find_elements(By.CLASS_NAME, 'banner')
for e in name_banner:
    banners.append(e.text)

# AL
years_american_league = []
links_american_league = []
al = [] # American League

blocks_am_le = driver.find_elements(By.CSS_SELECTOR,'.datacolBox a[title*="American League"]')

for i in blocks_am_le:
    years_american_league.append(i.text)
    links_american_league.append(i.get_attribute("href"))
    al.append("American League")