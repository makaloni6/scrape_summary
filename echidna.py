from selenium.webdriver.common.by import By
from selenium import webdriver

import os
from utils import login_data
from selenium.webdriver.chrome.options import Options
import random

class Echidna:
    def __init__(self, driver):
        self.driver = driver
        self.driver.implicitly_wait(10)
    def get_status(self):

        raise NotImplementedError

    def scrape(self):

        raise NotImplementedError


    def login(self, acc):
        try:
            email_input = self.driver.find_element(
                by=By.ID, value='ap_email')
            email_input.send_keys(login_data[acc]['ACC_MAIL'])
        except BaseException as e:
            pass

        try:
            password_input = self.driver.find_element(
                by=By.ID, value='ap_password')
            password_input.send_keys(login_data[acc]['ACC_PASS'])
        except BaseException as e:
            pass

        self.driver.find_element(by=By.ID, value='signInSubmit').click()
