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
import os

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

#columns AL
df_years_american_league = pd.DataFrame({
    "year": years_american_league,
    "league": al
    })
counter_columns(df_years_american_league, "df_years_american_league")

# NL
years_national_league = []
links_national_league = []
nl = []
blocks_na_le = driver.find_elements(By.CSS_SELECTOR, '.datacolBox a[href$="n.shtml"]')
for i in blocks_na_le:
    years_national_league.append(i.text)
    links_national_league.append(i.get_attribute("href"))
    nl.append("National League")

# columns NL
df_years_national_league = pd.DataFrame({
    "year": years_national_league,
    "league": nl
    })
counter_columns(df_years_national_league, 'df_years_national_league')

# add info about each year | American League Player Review
name_header = driver.find_element(By.XPATH, '//div[@class="ba-table"]//h2[contains(text(), "American League")]')

name_al_player_reviw = []
statistic = []
names = []
teams = []
value = []

#driver.get(links_american_league[0]) ------------------------------------ delete
wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

h2 = driver.find_element(By.CSS_SELECTOR, "td h2")

text = h2.text
year = re.search(r"\d{4}", text).group()

data_statistic = driver.find_element(By.CLASS_NAME, 'datacolBlue')
print(data_statistic.text) # Base on Balls

main_table = []

# links
for link in links_american_league:
    driver.get(link)
    blocks = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "ba-table")) # div class=ba-table
    )

    # blocks
    for block in blocks:
        try:
            h2 = block.find_elements(By.TAG_NAME, "h2")
            if not h2:
                continue
            #logging_check(h2[0], 'h2[0]') # print('h2[0]', h2[0].text) # not empty

            #year = re.search(r"\d{4}", h2[0].text).group() # h2[0].text.split()[0] -------------------- checking
            match = re.search(r"\d{4}", h2[0].text)
            if not match:
                continue
            year = match.group()
            logging_check(year, 'year') # it is ok not empty

            # name_of_league
            text_of_h2 = h2[0].text
            if 'American League' in text_of_h2:
                name_of_league = 'American League'
            elif 'National League' in text_of_h2:
                name_of_league = 'National League'
            else:
                name_of_league = None

            # name_of_review
            if 'Player Review' in text_of_h2:
                name_of_review = 'Player Review'
            elif 'Pitcher Review' in text_of_h2:
                name_of_review = 'Pitcher Review'
            elif 'Team Review' in text_of_h2:
                name_of_review = 'Team Review'
            else:
                name_of_review = None

            # avoid blocks
            header_text = h2[0].text.strip()
            allowed_blocks = ["Player Review", "Pitcher Review"]
            if not any(word in header_text for word in allowed_blocks):
                continue

            rows = block.find_elements(By.TAG_NAME, "tr")
            current_statistic = None
            for row in rows:
                row_class = row.get_attribute('class') or ''
                if 'banner' in row_class or 'header' in row_class:
                    continue
                #logging_check('row_class', row_class)

                cells = row.find_elements(By.TAG_NAME, "td")
                if not cells:
                    continue

                filter_first_cell = cells[0].get_attribute('class') or "" # <td class="datacolBoxC">83</td>
                if 'datacolBoxC' in filter_first_cell:
                    continue
                elif 'datacolBlue' in filter_first_cell:
                    current_statistic = cells[0].text.strip()
                else:
                    continue

                if not current_statistic: # --------------------------------- checking
                    continue

                name_cell_text = cells[1].text.strip() if len(cells) > 1 else ""
                if re.search(r"[A-Za-z0-9]+", name_cell_text):
                    name = name_cell_text
                else:
                    name = None

                team_cell_text = cells[2].text.strip() if len(cells) > 2 else ""
                if re.search(r"[A-Za-z]", team_cell_text):
                    team = team_cell_text
                else:
                    team = None

                value = cells[3].text.strip() if len(cells) > 3 else None

                main_table.append({
                    'year': year,
                    'name_of_league': name_of_league,
                    'name_of_review': name_of_review,
                    'statistic': current_statistic,
                    'name': name,
                    'team': team,
                    'value': value
                })
        except Exception as e:
            print("Error:", e)
            continue

df_main_table = pd.DataFrame(main_table)

counter_columns(df_main_table, 'df_main_table')

print(df_years_national_league["league"].unique())
print(df_years_american_league["league"].unique())
print(df_main_table["name_of_league"].unique())

driver.quit()

# recording
df_years_american_league.to_csv("db\\df_years_american_league.csv", index=False)
df_years_national_league.to_csv("db\\df_years_national_league.csv", index=False)
df_main_table.to_csv("db\\df_main_data_american_league.csv", index=False)