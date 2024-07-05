from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

import os
class Echidna:
    def __init__(self, driver):
        self.driver = driver
        self.driver.implicitly_wait(10)
    def get_status(self):

        raise NotImplementedError

    def scrape(self):

        raise NotImplementedError
    
    def login(self):
        try:
            email_input = self.driver.find_element(
                by=By.ID, value='ap_email')
            email_input.send_keys(os.environ['MAIL'])
        except BaseException as e:
            input()

        try:
            password_input = self.driver.find_element(
                by=By.ID, value='ap_password')
            password_input.send_keys(os.environ['PASS'])
        except BaseException as e:
            input()

        self.driver.find_element(by=By.ID, value='signInSubmit').click()
