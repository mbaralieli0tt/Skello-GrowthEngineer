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


class Googler:
    
    def __init__(self):
        self.initOutput()
        self.initSelenium()
        self.launchGoogler()
    
    def success(self, str):
        print(colored("SUCCESS: " + str, 'green'))
    
    def warning(self, str):
        print(colored("WARNING: " + str, 'yellow'))

    def failure(self, str):
        print(colored("FAILURE: " + str, 'red'))

    def initOutput(self):
        self.exportPath = "./data2.csv"
        if os.path.isfile(self.exportPath):
            self.df = pd.read_csv(self.exportPath)
        else:
            self.failure("File data.csv not found")
            sys.exit()
        
        if os.path.isfile("./companies.csv"):
            self.companies = pd.read_csv("./companies.csv")
        else:
            self.companies = pd.DataFrame(columns=(['url']))
        
        if os.path.isfile("./people.csv"):
            self.people = pd.read_csv("./people.csv")
        else:
            self.people = pd.DataFrame(columns=(['url']))

    def initSelenium(self):
        option = webdriver.ChromeOptions()
        option.add_argument('--lang=es-US')
        prefs = {'intl.accept_languages': 'es-US'}
        option.add_experimental_option("prefs",prefs)
        option.add_argument('--disable-blink-features=AutomationControlled')
        self.browser  = webdriver.Chrome(ChromeDriverManager().install(), options=option)
        self.success("Selenium have been initialized succesfully")
    
    def checkCookies(self):
        time.sleep(3)
        try:
            self.browser.find_element(By.XPATH, '//h1[contains(text(), "Antes de ir a Google")]')
            time.sleep(0.5)
            try:
                tmp = self.browser.find_element(By.XPATH, '//div[contains(text(), "Aceptar todo")]/parent::button')
                time.sleep(0.5)
                try:
                    tmp.click()
                    time.sleep(2)
                    self.success("Cookies button have been clicked successfully")
                except ElementClickInterceptedException:
                    self.failure("Can't click cookies button")
            except NoSuchElementException:
                self.warning("Can't find cookies button")
        except NoSuchElementException:
            self.warning("Apparently, no need to check cookies")

    def launchSearch(self, search):
        try:
            tmp = self.browser.find_element(By.XPATH, '//input[@class="gLFyf gsfi"]')
            time.sleep(0.5)
            try:
                tmp.click()
                time.sleep(0.5)
                try:
                    tmp.send_keys(search)
                    time.sleep(0.5)
                    try:
                        tmp.send_keys(Keys.ENTER)
                        time.sleep(1)
                        self.success("Search have been launched successfully")
                    except:
                        self.failure("Can't press enter")
                except:
                    self.failure("Can't send keys")
            except ElementClickInterceptedException:
                self.failure("Can't click search bar")
        except NoSuchElementException:
            self.failure("Can't find search bar")

    def getCity(self, s):
        if s != "No disponible":
            if s.endswith(")") == True:
                s = s[::-1]
                tmp = s.find("(")
                if tmp > 1:
                    s = s[1:tmp]
                    s = s[::-1]
                    return(s)
                else:
                    self.failure("I'm fucked")
            elif s.endswith(", España"):
                s = s.replace(", España", "")
                s = s[::-1]
                tmp = s.find(',')
                s = s[:tmp]
                s = s[::-1]
                return(s)
            elif s.endswith(",España"):
                s = s.replace(",España", "")
                s = s[::-1]
                tmp = s.find(',')
                s = s[:tmp]
                s = s[::-1]
                return(s)
            else:
                self.failure("WTF: " + s)
            return("No disponible")

    def parseResults(self):
        try:
            tmp = self.browser.find_elements(By.XPATH, '//div[@class="MjjYud"]/div/div/div/div/a')
            print(len(tmp))
            for t in tmp:
                link = t.get_attribute("href")
                if link.find("es.linkedin.com/") > 0 and link.find("www.google.com/search?q=") < 0:
                    if link not in self.people and link not in self.companies:
                        # print(link)
                        if link.find("/company/") > 0:
                            self.companies.loc[len(self.companies)] = [link]
                            print("Company: " + link)
                        else:
                            self.people.loc[len(self.people)] = [link]
                            print("People: " + link)
                    else:
                        self.warning("Link already saved")
        except NoSuchElementException:
            self.failure("No links found")
        

    def launchGoogler(self):
        search = ""

        self.browser.get("https://www.google.com")
        self.checkCookies()
        for idx, row in self.df.iterrows():
            self.browser.get("https://www.google.com")
            tmp = self.getCity(row['adress'])
            if tmp and tmp != "No disponible":
                search = row['name'] + " " + tmp + " linkedin"
                self.launchSearch(search)
                self.parseResults()
                
                self.people.to_csv("./people.csv", index=False, encoding="utf-8-sig", sep=",")
                self.companies.to_csv("./companies.csv", index=False, encoding="utf-8-sig", sep=",")
            else:
                self.warning("No city found")
            # input("Press enter for next iteration")
        
        input("Press enter to kill")

def main():
    g = Googler()

if __name__ == "__main__":
    main()