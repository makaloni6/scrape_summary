import os
from selenium import webdriver
from dotenv import load_dotenv
import subprocess
import csv
import pandas as pd
from tqdm import tqdm
import re
from echidna import Echidna
import glob
import pickle
import time
from utils import progress_checker, decrypt_code, limit, profile_data, get_driver_with_profile
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select

class OrdScraper(Echidna):

    def __init__(self, driver):
        super().__init__(driver)
        self.customer = pd.DataFrame(columns = ['Id', 'zip1', 'zip2', 'name', 'add0', 'add1', 'add2', 'phone', 'gift', 'codes', 'q', 'p_list'])
        self.result = pd.DataFrame(columns = ['Id', 'Result', 'Reason', 'Code'])

    def clear_cash(self) -> None:
        try:
            subprocess.run("pgrep 'chrome' | xargs kill -9", shell=True)
        except BaseException:
            pass
    
    def wait_for_element(self, driver, locator, timeout=10):
        wait = WebDriverWait(driver, timeout)
        element = wait.until(EC.presence_of_element_located(locator))
        return element
    
    def save_result(self, order_id, code, reason):
        self.result = pd.concat([self.result, pd.DataFrame([[order_id, '×', reason, decrypt_code]], columns=['Id', 'Result', 'Reason', 'Code'])], ignore_index=True)

    def save_pickle(self, name) -> None:
        with open(name, 'wb') as f:
            pickle.dump(self.customer, f)

    def load_pickle(self, name) -> pd.DataFrame:
        with open(name, 'rb') as f:
            data = pickle.load(f)
        return data

    def remove(self) -> None:
        try:
            self.driver.get(os.environ['REMOVE_URL'])
            del_btn = self.driver.find_elements(
                by=By.CSS_SELECTOR,
                value='span.a-size-small.sc-action-delete')
            for d in del_btn:
                d_b = self.driver.find_elements(
                    by=By.CSS_SELECTOR,
                    value='span.a-size-small.sc-action-delete')
                d_b[0].find_element(by=By.CSS_SELECTOR, value='input.a-color-link').click()
                time.sleep(1)
        except BaseException as e:
            self.save_result('remove:')

    def check_previous_order(self) -> pd.DataFrame:

        finished_order_id = pd.DataFrame(columns=['OrderID', 'Result', 'Reason', 'Code'])
        files = glob.glob(os.environ['RESULT_CSV'])
        pattern = r'([a-zA-Z0-9-]+-[0-9]+)'

        for file in files:
            df = pd.read_csv(file)
            df.columns = ['OrderID', 'Result', 'Reason', 'Code']
            df = df.drop(0).reset_index(drop=True)
            finished_order_id = pd.concat([finished_order_id, df], ignore_index=True)

        return finished_order_id
    
    def check_purchase(self, order_id, finished_order_id) -> bool:
        pattern = r'([a-zA-Z0-9-]+-[0-9]+)'
        normalized_id = re.findall(pattern, order_id)
        if normalized_id in finished_order_id['OrderID'].values:
            return True
        else:
            return False

    @progress_checker('ページチェック')
    def is_correct_page(self, code) -> bool:
        try:
            code_candidate =self.driver.find_element(
                by=By.ID, value='ASIN').get_attribute('value')
        except BaseException:
            return False
        
        if code != code_candidate:
            return False

        return True

    @progress_checker('上限チェック')
    def is_limit_page(self, code) -> bool:

        if code in limit:
            return True
        else:
            return False
    
    @progress_checker('routineチェック')
    def is_routine_page(self) -> bool:
        routine = self.driver.find_elements(by=By.CLASS_NAME, value='a-section.a-spacing-none.a-padding-none.accordion-caption')
        flag = True if len(routine) > 0 else False
        return flag
    
    @progress_checker('在庫チェック')
    def is_empty(self) -> bool:
        if len(self.driver.find_elements(by=By.ID, value='outOfStock')) > 0:
            return True
        else:
            return False
        
    
    @progress_checker('納期チェック')
    def is_available(self) -> bool:
        availability = self.find_element_safely((By.ID, 'availability'))
        if '一時的に在庫切れ' in availability.text:
            return False
        else:
            return True
    

    def find_element_safely(self, locator, timeout=3):
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
        except TimeoutException:
            return None

    @progress_checker('価格チェック')
    def price_check(self) -> int:
        coreprice = self.find_element_safely((By.ID, 'corePrice_feature_div'))
        if coreprice:

            price = self.driver.find_element(
                by=By.CLASS_NAME, value='a-offscreen')
            price = int(re.sub('[￥, ]', '', str(price.get_attribute('innerHTML'))))

        else:
            coreprice = self.find_element_safely((By.ID, 'corePriceDisplay_desktop_feature_div'))
            if coreprice:
                price = coreprice.find_element(
                    by=By.CLASS_NAME, value='a-section.a-spacing-none.aok-align-center')
                price = int(
                    re.sub(
                        '[￥, ]', '', str(
                            price.get_attribute('innerHTML'))))
            else:
                book_price = self.find_element_safely((By.ID, 'price'))
                if book_price:
                    price = int(
                        re.sub(
                            '[￥, ]', '', str(
                                book_price.text)))
                else:
                    return 0
    
        return price
    
    @progress_checker('クーポンチェック')
    def coupon_check(self):
        try:
            coupon = self.driver.find_element(
                by=By.CLASS_NAME, value='promoPriceBlockMessage')
            coupon_html = coupon.get_attribute('innerHTML')
            magic_n = re.findall('badgepctch([0-9]+)', coupon_html)[0]
            coupon_switch = coupon.find_element(
                by=By.ID, value='cbpctch{}'.format(magic_n))
            coupon_switch.click()

        except BaseException as e:
            print('クーポンなし')

    @progress_checker('個数チェック')
    def quantity_check(self, quantity):
        try:
            quant_dropdown = self.driver.find_element(By.ID, value='selectQuantity')
            rcx_quant = quant_dropdown.find_element(By.ID, value='quantity')
            quant_name = rcx_quant.find_elements(By.CSS_SELECTOR, value='option')
            quant_list = [row.text for row in quant_name]

            idx_quantity = 0
            for idx, q in enumerate(quant_list):
                
                if '数量の選択' in q:
                    continue
                q = re.findall(r'\d+', q)[0]
                if int(q) > quantity:
                    raise Exception
                if int(q) == quantity:
                    idx_quantity = idx
                    break
            select = Select(rcx_quant)
            select.select_by_index(idx_quantity)
            return True
        except BaseException as e:
            return False

    def click_add(self) -> bool:
        cart_btn = self.find_element_safely((By.ID,'submit.add-to-cart'))
        if cart_btn:
            cart_btn.find_element(
                    by=By.ID,
                    value='add-to-cart-button').click()
            return True
        else:
            time.sleep(2)
            cart_btn = self.find_element_safely((By.ID, 'add-to-cart-button'))
            if cart_btn:
                cart_btn.click()
                return True
            else:
                return False
            
            
    def go_cart(self):
        go_cart = self.find_element_safely((By.ID,'attach-view-cart-button-form'))
        if go_cart:
            go_cart.find_element(
                by=By.CSS_SELECTOR,
                value='input.a-button-input').click()
            return True
        else:
            return False

            

    def add_box(self, order_id, code, p, q):

        self.driver.get(os.environ['TEMP_URL'].format(code))
        if not self.is_correct_page(code):
            self.save_result(order_id, code, '正しいページを参照できていません。')
            return False
        
        if self.is_limit_page(code):
            self.save_result(order_id, code, '上限に該当しています。')
            return False
        
        if self.is_routine_page():
            self.save_result(order_id, code, 'routine')
            return False
        
        if self.is_empty():
            self.save_result(order_id, code, '在庫がないため終了。')
            return False
        
        p_comp = self.price_check()
        if p_comp == 0:
            self.save_result(order_id, code, '価格を取得できませんでした。')
            return False
        
        if p_comp > p:
            self.save_result(order_id, code, '価格が高いため終了。')
            return False
        
        if not self.is_available():
            self.save_result(order_id, code, '納期が遅いため終了。')
            return False
        
        self.coupon_check()
        if not self.quantity_check(q):
            self.save_result(order_id, code, '個数を設定できませんでした。')
            return False
        
        if not self.click_add():
            self.save_result(order_id, code, 'カートに追加できませんでした。')
            return False

        self.go_cart()

    def pay(self):
        pass


    def scrape_base(self) -> None:
        code_num = 8
        price_num = -1
        name_num = -9
        count = 0

        for idx, order in tqdm(self.customer.iterrows(), total=len(self.customer)):

            code_price = {}
            print('key, value')
            print(order['Id'], order['codes'])
            for code, price in zip(order['codes'], order['p_list']):
                acc_name = order['Id'][:name_num]
                url = os.environ['CHECK_URL'].format(acc_name, code.lower())
                
                self.driver.get(url)

                time.sleep(2)

                iframe = self.driver.find_element(
                    by=By.TAG_NAME,
                    value='body'
                )

                time.sleep(2)

                innerHTML = iframe.get_attribute('innerHTML')

                code = re.findall('識別コード:([0-9A-Z]{10})', innerHTML)[0]
                code = decrypt_code(code)

                self.driver.switch_to.default_content()

                if price == '':
                    self.save_result('price is not set.')
                    continue

                if code in code_price:
                    code_price['DUPLICATE'] = int(price)
                else:
                    code_price[code] = int(price)
            print(code_price)
            order['p_list'] = code_price
            self.customer.loc[idx] = order
            count += 1
            time.sleep(3)

    def scrape(self) -> None:

        finished_order_id = self.check_previous_order()

        for idx, order in tqdm(self.customer.iterrows(), total=len(self.customer)):
            if self.check_purchase(order['Id'], finished_order_id):
                print('skipped:{}'.format(order['Id']))
                continue
            
            self.remove()
            
            in_check = 0
            for idx, code in enumerate(order['p_list'].keys()):

                p = order['p_list'][code]
                q = order['q'][idx]

                print('buying...{}, asin:{}, price:{}, quantity:{}'.format(
                    order['Id'], code, p, q))
            
                self.add_box(order['Id'], code, p, q)
                print(self.result)
                in_check += 1
                
            self.pay()

                

class RtScraper(Echidna):

    def __init__(self, driver):
        super().__init__(driver)
        self.customer = {}
        self.result = {}

    def save_result(self, order_id,reason) -> None:
        if order_id not in self.result.keys():
            self.result[order_id] = reason

    def scrape(self):
        pass


def main():
    load_dotenv()
    print('account?\nlayschips:0\nyamasakimara:1\nguguru:2\nshisononororo:3\nasutarisuku:4\nkuronoushin:5\nbyakuyamagan:6\nhanihkamukeiko:7\nkeikeikofr:8\nmt4mailmt4:9\nmikamangadays:10\nyamanekuroba:11\nadayinthelife:12')
    acc = int(input('->'))
    mode = input('init:0, continue:1, stockfile:2, move_file:3->')
    
    driver = get_driver_with_profile(
        profile_data[acc]['PROFILE_DIR'], profile_data[acc]['PROFILE_PATH']
    )
    OS = OrdScraper(driver)
    # OS.clear_cash()
    OS.data_setter()

    # RS = RtScraper(driver)
    # RS.data_setter()

    if mode == '0':
        OS.scrape_base()
        OS.save_pickle('save.pickle')
        OS.scrape()
        # RS.scrape()

    elif mode == '1':
        OS.customer = OS.load_pickle(os.environ['SAVEDATA'])
        OS.scrape()
        # RS.scrape()


    elif mode == '2':
        filename = input('filename?->')
        # br.csv_reader_recover()
        # br.recovery(filename)

    elif mode == '3':
        OS.rename_cp_rm()
    
    # csvを作成するプログラム

    print('Finished!!\n')


if __name__ == '__main__':
    main()
