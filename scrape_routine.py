import os
import time
from selenium import webdriver
from dotenv import load_dotenv
from echidna import Echidna
from selenium.webdriver.common.by import By


    
class RoutineScraper(Echidna):
    def __init__(self, driver):
        super().__init__(driver)
        self.subscriptions_url = os.environ['SUBS_URL']

    def cancelSubs(self):
        self.driver.get(self.subscriptions_url)

        if 'signin' in self.driver.current_url:
            self.login()
        


        subscription_elements = self.driver.find_elements(
            by=By.CLASS_NAME,
            value='a-section.subscription-card.aok-inline-block.subscription-hover-state-container'
        )
        print('要素数:{}'.format(len(subscription_elements)))
        input()
        for subscription in subscription_elements:
            self.checkOut(subscription)

    def checkOut(self, element):
        pass



    def test(self, product_id: str) -> None:
        self.driver.get(os.environ['TEMP_URL'].format(product_id))
        self.driver.quit()


    def helloworld(self):
        print('hello world')


def get_driver_with_profile(dir_path, profile_path,) -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument(f'--user-data-dir={dir_path}')
    options.add_argument(f'--profile-directory={profile_path}')
    driver = webdriver.Chrome(options=options)
    return driver


def main():
    load_dotenv()
    driver = get_driver_with_profile(
        os.environ['PROFILE_DIR'], os.environ['PROFILE_PATH']
    )
    RS = RoutineScraper(driver)
    RS.cancelSubs()


if __name__ == '__main__':
    main()