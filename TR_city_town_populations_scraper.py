import os
import time 
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup 
import pandas as pd

option = webdriver.ChromeOptions()
option.add_argument("--incognito")
option.add_argument("--start-maximized")

driver_path = r"C:/Users/caner/OneDrive/Desktop/Course Notebooks/Elektrik Proje/chromeWebDriver/chromedriver.exe"

main_url = "https://www.nufusu.com/"
browser = webdriver.Chrome(executable_path=driver_path, options=option)
browser.get(main_url)

content = browser.page_source # assign source code to 
soup = BeautifulSoup(content, features="lxml") # soup ile unstructured source kodu tuttuk

tables = soup.find_all("table", {"class" : "pure-table pure-table-bordered pure-table-striped"})
city_dic_2020 = {}   # {city_name:city_url_2020}   {'İstanbul': 'https://www.nufusu.com//il/istanbul-nufusu', ... }
city_dic_2019 = {}   # {city_name:city_url_2019}   {'İstanbul': 'https://www.nufusu.com/il/2019/istanbul-nufusu', ... }
for table in tables:
    if "İl" in table.text: # get the correct table 
        row_tags_trs = table.find_all("tr")[1:]          # first column row is skipped
        for row_tag_tr in row_tags_trs:                  # type = 'bs4.element.Tag'
            city_tag_td = row_tag_tr.find_all("td")[1]   # get city tag
            city_name = city_tag_td.text                 # get city name from tag         


            # get "a" tag under "td" tag of clickable city element. This row is like dict. , so get "href" key's value by dic. get() method
            city_link_end_2020 = city_tag_td.find("a").get("href", "Key Not Found")         # 1st exp: /il/istanbul-nufusu'
            city_url_2020 = main_url + city_link_end_2020
            city_dic_2020[city_name] = city_url_2020   # 2020 page links are gathered to city_dic_2020

            # 2019 page links are gathered to city_dic_2019
            city_link_end_2019 = city_link_end_2020[1:4] + "2019/" + city_link_end_2020[4:] # il/2019/istanbul-nufusu'
            city_url_2019 = main_url + city_link_end_2019
            city_dic_2019[city_name] = city_url_2019

# Scraping 2019 İlçe(county) Data 
dataframes2019 = []
for city, city_link in city_dic_2019.items() :
    browser.get(city_link)
    content_city = browser.page_source # source kodu content değişkeninde tuttuk
    soup_city = BeautifulSoup(content_city, features="lxml") # soup ile unstructured source kodu tuttuk

    time.sleep(3)
    tables = soup_city.find_all("table", {"class" : "pure-table pure-table-bordered pure-table-striped"})
    col_names = []
    df_data = []

    for table in tables:
        if "Toplam Nüfus" in table.text:
            col_row = table.find_next("tr")

            for col in col_row.find_all("th"):
                col_names.append(col.text)

            row_ids = table.find_all("tr")
            for row_id in row_ids:
                row_data = []

                for row_value in row_id.find_all("td"):
                    row_data.append(row_value.text)

                if row_data != []:  # eliminate null rows generated in the beginning and end of loop
                    df_data.append(row_data)                  
    df = pd.DataFrame(df_data, columns=col_names)
    df["Şehir"] = city
    df = df.drop(columns=["Erkek Nüfusu", "Kadın Nüfusu"])
    df = df.rename(columns={"Toplam Nüfus":"İlçe Nüfusu"})
    dataframes2019.append(df)

df2019 = pd.concat(dataframes2019, axis=0)
file_name = f"df2019.csv"
save_path = r"C:\Users\caner\OneDrive\Desktop\Course Notebooks\Elektrik Proje\Code\Scraping\Nüfus_data"
df2019.to_csv(path_or_buf=os.path.join(save_path,file_name), index=False)

# Scraping 2020 İlçe Data 
dataframes2020 = []
for city, city_link in city_dic_2020.items() :
    browser.get(city_link)
    content_city = browser.page_source  # source code assigned to variable "content_city"
    soup_city = BeautifulSoup(content_city, features="lxml") # parsed source code assigned to "soup_city"

    time.sleep(3)
    tables = soup_city.find_all("table", {"class" : "pure-table pure-table-bordered pure-table-striped"})
    col_names = []
    df_data = []

    for table in tables:
        if "İlçe Nüfusu" in table.text:
            col_row = table.find_next("tr")

            for col in col_row.find_all("th"):
                col_names.append(col.text)

            row_ids = table.find_all("tr")
            for row_id in row_ids:
                row_data = []

                for row_value in row_id.find_all("td"):
                    row_data.append(row_value.text)

                if row_data != []:  # eliminate null rows generated in the beginning and end of loop
                    df_data.append(row_data)                  
    df = pd.DataFrame(df_data, columns=col_names)
    df["Şehir"] = city
    df = df.drop(columns=["Erkek Nüfusu", "Kadın Nüfusu"])
    dataframes2020.append(df)

df2020 = pd.concat(dataframes2020, axis=0)
file_name = f"df2020.csv"
save_path = r"C:\Users\caner\OneDrive\Desktop\Course Notebooks\Elektrik Proje\Code\Scraping\Nüfus_data"
df2020.to_csv(path_or_buf=os.path.join(save_path,file_name), index=False)

#concatenating df2019 and df2020 and manipulating our last dataframe "df_all"
df_all = pd.concat([df2019, df2020], axis=0)
df_all["Nüfus Yüzdesi"] = df_all["Nüfus Yüzdesi"].str.replace("% ", "").str.replace(",", ".").astype(float)
df_all["İlçe Nüfusu"] = df_all["İlçe Nüfusu"].astype(str).str.replace(".", "").astype(int)
path_name = r"C:\Users\caner\OneDrive\Desktop\Course Notebooks\Elektrik Proje\Code\Scraping\Nüfus_data\İlçe_Nüfusları_2019-2020.csv"
df_all.to_csv(path_or_buf=path_name, index=False)

