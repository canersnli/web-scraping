# This code has been rated at 9.85/10
# Name: pylint
# Version: 2.17.2

"""
This is a selenium bot script that downloads excel files one by one that hold
historical electricity generation data of dams in Turkey.
"""

import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

option = webdriver.ChromeOptions()
option.add_argument("--incognito")
option.add_argument("--start-maximized")
# option.add_argument("--no-startup-window")

DRIVER_PATH = r"Electricity_Project/chromeWebDriver/chromedriver.exe"

browser = webdriver.Chrome(executable_path=DRIVER_PATH, options=option)
browser.get(
 "https://seffaflik.epias.com.tr/transparency/uretim/gerceklesen-uretim/gercek-zamanli-uretim.xhtml"
)

START_DATE = "01.01.2019"
END_DATE = "22.08.2021"
RELOAD_PAGE = False
# Gathering ids of not downloaded files, in case any station's file is not downloaded
not_downloaded_list = []
# santral id to begin with in case restarting process after error
START_ID = 1


REFRESH_THRESHOLD = 6
# This is a self-discovered trick that avoids detection of my scraper bot. Each time number of
# "REFRESH_THRESHOLD" files were downloaded, it refreshes page in order to avoid to be detected
# as scraper by web-site host. In case host detects my scraper bot, it throws warning: "Passthrough
# is not supported, GL is disabled" , causes drastically long awaiting times which leads
# TimeoutExceptions eventually eventhough I set very long webdriver waiting times between processes.

for i in range(START_ID, 1779):

    if RELOAD_PAGE:
        i = i-1

    if (((i - START_ID) % REFRESH_THRESHOLD == 0) & (i != START_ID)) | (RELOAD_PAGE is True):
        # Refresh the page every time "REFRESH_THRESHOLD" number of files are downloaded
        time.sleep(8)
        browser.quit()
        time.sleep(2)
        browser = webdriver.Chrome(executable_path=DRIVER_PATH, options=option)
        browser.get(
            "https://seffaflik.epias.com.tr/transparency/uretim/gerceklesen-uretim/gercek-zamanli-uretim.xhtml"
        )
        RELOAD_PAGE = False

    try:
        santral_dropdown = WebDriverWait(browser, 30).until(
            EC.presence_of_element_located((By.ID, "j_idt219:powerPlant")))
        santral_dropdown.click()

    except TimeoutException as t:
        print(
            f"{i} \nTimeoutException is occured while santral_dropdown menu was loading")
        not_downloaded_list.append(i)
        RELOAD_PAGE = True

    try:
        santral_name = WebDriverWait(browser, 30).until(
            EC.element_to_be_clickable((By.ID, "j_idt219:powerPlant_" + str(i)))
        )
        santral_name.click()

    except TimeoutException as t:
        print(f"{i} \nTimeoutException is occured at santral_name selection. ")
        not_downloaded_list.append(i)
        RELOAD_PAGE = True

    # type dates and click "uygula"
    try:
        time.sleep(1)
        browser.execute_script(
            f"document.getElementById('j_idt219:date1_input').value = '{START_DATE}'"
        )
        time.sleep(1)
        browser.execute_script(
            f"document.getElementById('j_idt219:date2_input').value = '{END_DATE}'"
        )
        uygula_button = WebDriverWait(browser, 30).until(
            EC.element_to_be_clickable((By.ID, 'j_idt219:goster'))
        )
        # uygula_button = browser.find_element_by_id('j_idt219:goster')
        uygula_button.click()

    except TimeoutException as t:
        print(f"{i} \nTimeoutException is occured at clicking 'uygula' ")
        not_downloaded_list.append(i)
        RELOAD_PAGE = True

    try:
        # , ignored_exceptions="NoSuchElementException"
        wait = WebDriverWait(browser, timeout=200)
        download_button = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "a[onclick*=mojarra]"))
        )
        download_button.click()

    except NoSuchElementException as n:
        print(
            f"NoSuchElementException: Download button can not be located for PowerPlant number {i}"
        )
        not_downloaded_list.append(i)
        RELOAD_PAGE = True

    except TimeoutException as t:
        print(
            f"{i} \nTimeoutException is occured at waiting 'download' button to be clickable"
        )
        not_downloaded_list.append(i)
        RELOAD_PAGE = True

    print(i)
    print('powerPlant_'+str(i)+" data has been downloaded successfully")
    # print(santral.get_attribute("data-label"))
print(not_downloaded_list)
