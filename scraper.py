import numpy as np
from pprint import pprint
import pandas as pd
from random import *
import sys
import json
import time
import os
import gspread
from datetime import datetime
from tqdm import tqdm
from termcolor import colored
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium import *
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys


class Scraper:
    
    def __init__(self, tag):
        self.links = []

        self.name = ""
        self.url = ""
        self.activity = 0
        self.CIF = ""
        self.date = ""
        self.sector = ""
        self.tag = tag
        self.adress = ""
        self.tel = ""
        self.website = ""
        self.TVA = ""

        self.initOutput()
        self.initSelenium()
        self.launchCrawling(self.tag)
    
    def success(self, str):
        print(colored("SUCCESS: " + str, 'green'))
    
    def warning(self, str):
        print(colored("WARNING: " + str, 'yellow'))

    def failure(self, str):
        print(colored("FAILURE: " + str, 'red'))

    def initOutput(self):
        self.exportPath = "./data.csv"
        if os.path.isfile(self.exportPath):
            self.df = pd.read_csv(self.exportPath)
        else:
            self.df = pd.DataFrame(columns=(['url', 'name', 'isActive', 'CIF', 'date', 'sector', 'tag', 'adress', 'tel', 'website', 'TVA']))

    def initSelenium(self):
        option = webdriver.ChromeOptions()
        option.add_argument('--disable-blink-features=AutomationControlled')
        self.browser  = webdriver.Chrome(ChromeDriverManager().install(), options=option)
        self.success("Selenium have been initialized succesfully")
    
    def checkCookies(self):
        time.sleep(3)
        try:
            tmp = self.browser.find_element(By.XPATH, '//button[@class="btn teal cookies-cta cookies-accept-cta"]')
            try:
                tmp.click()
                time.sleep(2)
                self.success("Cookies button have been clicked successfully")
            except ElementClickInterceptedException:
                self.warning("Can't click cookies button")
        except NoSuchElementException:
            self.warning("Cookies button not found")

    def loadMoreResults(self):
        self.browser.execute_script("window.scrollTo(0, 1080)")
        time.sleep(3)
        try:
            tmp = self.browser.find_element(By.XPATH, '//div[@class="show-more-data"]/div/button')
            try:
                time.sleep(1)
                tmp.click()
                time.sleep(2)
                self.success("Load more button have been clicked successfully")
            except ElementClickInterceptedException:
                self.warning("Can't click load more button")
        except NoSuchElementException:
            self.warning("Load more button not found")

    def getLinks(self):
        try:
            tmp = self.browser.find_elements(By.XPATH, '//li[@class="li-item"]/a')
            for t in tmp:
                u = t.get_attribute("href")
                self.links.append(u)
        except NoSuchElementException:
            self.failure("No links found")

    def getActivity(self):
        try:
            self.browser.find_element(By.XPATH, '//span[@class="company-status-text activa-text"]')
            self.success("Is active")
            self.activity = 1
        except NoSuchElementException:
            self.warning("Seems inactive")
            try:
                self.browser.find_element(By.XPATH, '//span[@class="company-status-text extinta-text"]')
                self.success("Is Inactive")
                self.activity = 0
            except NoSuchElementException:
                self.failure("Neither active or inactive")
                self.activity = -1

    def getName(self):
        try:
            tmp = self.browser.find_element(By.XPATH, '//h1')
            self.name = str(tmp.text)
        except NoSuchElementException:
            self.warning("Name not found")

    def getCif(self):
        try:
            tmp = self.browser.find_element(By.XPATH, '//ul[@class="collection list list-company-data no-border"]/li[1]/span[2]')
            cif = str(tmp.text)
            cif = cif[9:]
            self.CIF = cif
        except NoSuchElementException:
            self.warning("CIF not found")

    def getDate(self):
        try:
            tmp = self.browser.find_element(By.XPATH, '//ul[@class="collection list list-company-data no-border"]/li[2]/span[2]')
            self.date = str(tmp.text)
        except NoSuchElementException:
            self.warning("Date not found")

    def getSector(self):
        try:
            tmp = self.browser.find_element(By.XPATH, '//ul[@class="collection list list-company-data no-border"]/li[3]/span[2]')
            self.sector = str(tmp.text)
        except NoSuchElementException:
            self.warning("Sector not found")

    def getAdress(self):
        try:
            tmp = self.browser.find_element(By.XPATH, '//ul[@class="collection list list-company-data no-border"]/li[4]/p/span')
            self.adress = str(tmp.text)
        except NoSuchElementException:
            self.warning("Adress not found")

    def getTel(self):
        try:
            tmp = self.browser.find_element(By.XPATH, '//ul[@class="collection list list-company-data no-border"]/li[5]/span')
            tel = str(tmp.text)
            tel = tel[10:]
        except NoSuchElementException:
            self.warning("Tel not found")

    def getWebsite(self):
        try:
            tmp = self.browser.find_element(By.XPATH, '//ul[@class="collection list list-company-data no-border"]/li[6]/span')
            web = str(tmp.text)
            web = web[5:]
            self.website = web
        except NoSuchElementException:
            self.warning("Website not found")

    def getTVA(self):
        try:
            tmp = self.browser.find_element(By.XPATH, '//ul[@class="collection list list-company-data no-border"]/li[7]/p/a')
            try:
                tmp.click()
                self.success("IVA = " + str(tmp.text))
                self.TVA = str(tmp.text)
            except ElementClickInterceptedException:
                self.failure("Can't click to get tva")
        except NoSuchElementException:
            self.warning("IVA not found")

    def getData(self):
        self.getName()
        self.getActivity()
        self.getCif()
        self.getDate()
        self.getSector()
        self.getAdress()
        self.getTel()
        self.getWebsite()
        if self.activity == 1 and self.sector == "Hostelería":
            self.df.loc[len(self.df)] = [self.url if len(self.url) > 1 else np.nan, self.name if len(self.name) > 1 else np.nan, self.activity, self.CIF if len(self.CIF) > 1 else np.nan, self.date if len(self.date) > 1 else np.nan, self.sector if len(self.sector) > 1 else np.nan, self.tag if len(self.tag) > 1 else np.nan, self.adress if len(self.adress) > 1 else np.nan, self.tel if len(self.tel) > 1 else np.nan, self.website if len(self.website) > 1 else np.nan, "TVA"]
            self.df.to_csv(self.exportPath, index=False, encoding="utf-8-sig", sep=",")
            print(self.df)

    def scrap(self):
        i = 0
        for l in self.links:
            if l not in self.df:
                print(str(i) + "/" + str(len(self.links)))
                i = i + 1
                self.url = l
                self.browser.get(l)
                time.sleep(1)

                try:
                    tmp = self.browser.find_element(By.XPATH, '//div[@class="center-align btn-detalle"]/a')
                    self.browser.get(tmp.get_attribute("href"))
                    time.sleep(1)
                except NoSuchElementException:
                    self.warning("No need to click")
                self.getData()
            else:
                self.warning("Link already saved")

    def launchCrawling(self, tag):
        self.browser.get("https://www.infoempresa.com/es-es/es/buscar?gateway_id=ESP_0000&q=" + tag)
        self.checkCookies()
        self.loadMoreResults()
        self.getLinks()
        self.scrap()
        input("Press enter to kill")

def main(argv):
    s = Scraper(argv[1])

if __name__ == "__main__":
    main(sys.argv)