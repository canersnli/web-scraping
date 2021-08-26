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

option = webdriver.ChromeOptions()
option.add_argument("--incognito")
option.add_argument("--start-maximized") #
#option.add_argument("--no-startup-window")

driver_path = r"C:/Users/caner/OneDrive/Desktop/Course Notebooks/Elektrik Proje/chromeWebDriver/chromedriver.exe"

browser = webdriver.Chrome(executable_path=driver_path, options=option)
browser.get("https://seffaflik.epias.com.tr/transparency/uretim/gerceklesen-uretim/gercek-zamanli-uretim.xhtml")


start="01.01.2019"
end="22.08.2021"
reload_page = False
not_downloaded_list = []         # Gathering ids of not downloaded files, in case any station's file is not downloaded 
start_id = 1                     # santral id to begin with in case restarting process after error

refresh_threshold = 6            # This is a self-discovered trick that avoids detection of my scraper bot. Each time number of "refresh_threshold" files
                                 # were downloaded, it refreshes page in order to avoid to be detected as scraper by web-site host. In case host detects
                                 # my scraper bot, it throws warning: "Passthrough is not supported, GL is disabled" , causes drastically long awaiting
                                 # times which leads TimeoutExceptions eventually eventhough I set very long webdriver waiting times between processes.

for i in range(start_id,1779):

    if reload_page:
        i = i-1

    if  (( (i - start_id) % refresh_threshold == 0 ) & (i != start_id )) | (reload_page==True): 
        # Refresh the page every time "refresh_threshold" number of files are downloaded
        time.sleep(8) 
        browser.quit()
        time.sleep(2)
        browser = webdriver.Chrome(executable_path=driver_path, options=option)
        browser.get("https://seffaflik.epias.com.tr/transparency/uretim/gerceklesen-uretim/gercek-zamanli-uretim.xhtml")
        reload_page=False

    try:
        santral_dropdown = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.ID, "j_idt219:powerPlant")))
        santral_dropdown.click() 
    except TimeoutException as t:
        print(f"{i} \nTimeoutException is occured while santral_dropdown menu was loading")
        not_downloaded_list.append(i)
        reload_page = True
        continue

    try:
        santral_name = WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.ID, "j_idt219:powerPlant_" + str(i))))
        santral_name.click()
    except TimeoutException as t:
        print( f"{i} \nTimeoutException is occured at santral_name selection. ")
        not_downloaded_list.append(i)
        reload_page = True
        continue


    # type dates and click "uygula"
    try:
        time.sleep(1)
        browser.execute_script(f"document.getElementById('j_idt219:date1_input').value = '{start}'")
        time.sleep(1)
        browser.execute_script(f"document.getElementById('j_idt219:date2_input').value = '{end}'")   
        uygula_button = WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.ID, 'j_idt219:goster')))
        # uygula_button = browser.find_element_by_id('j_idt219:goster')
        uygula_button.click()
    except TimeoutException as t:
        print( f"{i} \nTimeoutException is occured at clicking 'uygula' ")
        not_downloaded_list.append(i)
        reload_page = True
        continue

    try:
        wait = WebDriverWait(browser, timeout=200)  #, ignored_exceptions="NoSuchElementException"
        download_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[onclick*=mojarra]")))
        download_button.click()
    except NoSuchElementException as n:
        print(f"NoSuchElementException: Download button can not be located for PowerPlant number {i}" )
        not_downloaded_list.append(i)
        reload_page = True
        continue
    except TimeoutException as t:
        print(f"{i} \nTimeoutException is occured at waiting 'download' button to be clickable")
        not_downloaded_list.append(i)
        reload_page = True
        continue
        
    print(i)  
    print('powerPlant_'+str(i)+" data has been downloaded successfully")
    #print(santral.get_attribute("data-label"))
print(not_downloaded_list)
