from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import time
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
driver = webdriver.Chrome(chrome_options=options)


##### Please insert the link, that is displayed in the browsers adressbar after you selected your search parameters. For example:
driver.get("https://www.service4mobility.com/mannheim/MobilitySearchServlet?identifier=MANNHEI01&kz_bew_pers=S&kz_bew_art=OUT&sprache=de&studj_id=3481")
time.sleep(1)
submitButton = driver.find_element(By.ID,"submitButton")
driver.execute_script("arguments[0].click();", submitButton)
#Liste mit allem wählen
time.sleep(3)
sel = Select(driver.find_element(By.XPATH, "//select[@name='DataTables_Table_0_length']"))
sel.select_by_visible_text("All")
time.sleep(0.8)


page_source = driver.page_source

from bs4 import BeautifulSoup
import pandas as pd

####Tabelle extrahieren

soup = BeautifulSoup(page_source, 'lxml')
table = soup.find('table', class_='datatable dataTable')
df = pd.DataFrame(columns=['Link', 'Heimathochschule', 'Land', 'Ort', 'Partnerhochschule', 'Studiengang', 'Programm'])
for row in table.tbody.find_all('tr'):    
    # Find all data for each column
    columns = row.find_all('td')
    
    link = 'https://www.service4mobility.com' + columns[0].find_all('a')[0]['href']
    hh = columns[1].text.strip()
    land = columns[2].text.strip()
    ort = columns[3].text.strip()
    ph = columns[4].text.strip()
    sg = columns[5].text.strip()
    pg = columns[6].text.strip()
    sp = columns[7].text.strip()

    df = df.append({'Link': link,  'Heimathochschule': hh, 'Land': land, 'Ort': ort, 'Partnerhochschule': ph, 'Studiengang': sg, 'Programm': pg, 'Sprache': sp}, ignore_index=True)


#Zu jeder Partneruni die Sprachnachweise und die Website aussuchen
for index, row in df.iterrows():
    url = row['Link']
    driver.get(url)
    time.sleep(1)
    page_source = driver.page_source
    soup1 = BeautifulSoup(page_source, 'lxml')
    for row in soup1.find_all('tr'):
        columns = row.find_all('td')
        if not columns[0].has_attr('class'):
            continue
        if columns[0].find('b') and columns[0]['class'] == ['colLabel']:
            print(columns[0].find('b').text + "  " + columns[1].text)
            if columns[0].find('b').text == 'Zugelassene Sprachnachweise' and df.loc[index, 'Link'] == url:
                df.loc[index, 'Sprachnachweise'] = columns[1].text
            elif columns[0].find('b').text == 'Website der Partneruniversität' and df.loc[index, 'Link'] == url:
                df.loc[index, 'Website'] = columns[1].text
            
    
    df.to_csv('out.csv')   
    time.sleep(0.00001)
  
