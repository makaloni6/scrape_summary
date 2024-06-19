import os
from selenium import webdriver
from dotenv import load_dotenv
import subprocess
import csv
import pandas as pd
from echidna import Echidna
from selenium.webdriver.chrome.options import Options

class OrdScraper(Echidna):

    def __init__(self, driver):
        super().__init__(driver)
        
        self.customer = {}
        # self.subscriptions_url = os.environ['SUBS_URL']

    def clear_cash(self) -> None:
        try:
            subprocess.run("pgrep 'chrome' | xargs kill -9", shell=True)
        except BaseException:
            pass

    def fileReader(self, filename) -> pd.DataFrame:
        df = pd.read_csv(os.environ['PASS1'] + filename)
        return df

    def dataSetter(self) -> dict:
        files = os.listdir(os.environ['PASS1'])
        main_files = [f for f in files if 'autoprice' not in f]
        sub_files = [f for f in files if 'autoprice' in f]

        for filename in sub_files:
            customerDf = self.fileReader(filename)
            for data in customerDf:
                pass

        for filename in main_files:
            customerDf = self.fileReader(filename)
            for data in customerDf:
                pass
    
    def wait_for_element(driver, locator, timeout=10):
        wait = WebDriverWait(driver, timeout)
        element = wait.until(EC.presence_of_element_located(locator))
        return element
        
    def optionSetter(self) -> dict:
        options = self.loadOptions()
        return webdriver.Chrome(options=options)
    
    def scrape_base(self):
        pass

    def main(self, mode):

        self.clear_cash()
        self.customer = self.dataSetter()
        self.driver = self.optionSetter()

        if mode = '0':
            self.scrape_base()
        elif mode = '1':
            self.open_pickle(os.environ['SAVEDATA'])
        
        processedData = self.loadProcessedData()
