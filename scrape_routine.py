import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

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
        
        # 要素が確認できるまで待機

        subscription_elements = self.driver.find_elements(
            by=By.CLASS_NAME,
            value='a-section.subscription-card.aok-inline-block.subscription-hover-state-container'
        )
        print('要素数:{}'.format(len(subscription_elements)))
        time.sleep(2)
        for idx in range(len(subscription_elements)):
            element = self.driver.find_elements(
                by=By.CLASS_NAME,
                value='a-section.subscription-card.aok-inline-block.subscription-hover-state-container'
            )
            self.checkOut(element[0])
            time.sleep(2)
            self.driver.get(self.subscriptions_url)
            time.sleep(2)

    def checkOut(self, element):
        element.click()
        pane = self.driver.find_element(By.CLASS_NAME, 'a-modal-scroller.a-declarative')
        right_pane = pane.find_element(By.CLASS_NAME, 'subActionMenu.leftShadow.shadowOverlay')
        time.sleep(2)
        try:
            cancel_bt = right_pane.find_elements(By.CLASS_NAME, 'a-row.actionContent')[-1]
            cancel_bt.click()
        except BaseException as e:
            print(e)

        pane = self.driver.find_element(By.CLASS_NAME, 'subActionContent')
        time.sleep(2)
        try:
            cancel_bt = pane.find_element(By.CSS_SELECTOR, 'input.a-button-input[type="submit"][aria-labelledby="confirmCancelLink-announce"]')
            cancel_bt.click()
        except BaseException as e:
            print(e)


    def test(self, product_id: str) -> None:
        self.driver.get(os.environ['TEMP_URL'].format(product_id))
        self.driver.quit()


    def helloworld(self):
        print('hello world')


def get_driver_with_profile(dir_path, profile_path) -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

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