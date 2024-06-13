import os
from selenium import webdriver
from dotenv import load_dotenv


class Echidna:
    def __init__(self, driver):
        self.driver = driver
    
    def get_status(self):

        raise NotImplementedError

    def scrape(self):

        raise NotImplementedError
    


class RoutineScraper(Echidna):
    def __init__(self, driver):
        super().__init__(driver)
        self.subscriptions_url = os.environ['SUBS_URL']

    def cancelSubs(self):
        self.driver.get(self.subscriptions_url)
        subscription_elements = self.driver.find_elements(...)
        
        for subscription in subscription_elements:
            self.checkOut(subscription)

    def checkOut(self, element):
        pass

    def helloworld():
        print('hello world')


if __name__ == '__main__':
    driver = webdriver.Chrome()
    load_dotenv()
    RS = RoutineScraper(driver)
    # RS.helloworld()