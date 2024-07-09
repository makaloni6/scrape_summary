from selenium.webdriver.common.by import By
from selenium import webdriver

import os
from utils import login_data
from selenium.webdriver.chrome.options import Options
import random
import pandas as pd
import unicodedata

class Echidna:
    def __init__(self, driver):
        self.driver = driver
        self.driver.implicitly_wait(10)
        
    def get_status(self):

        raise NotImplementedError

    def scrape(self):

        raise NotImplementedError

    def fileReader(self, filename) -> pd.DataFrame:

        encodings = ['utf-8', 'shift-jis', 'cp932']
        for encoding in encodings:
            try:
                df = pd.read_csv(os.environ['PASS1'] + filename, encoding=encoding, dtype=str)
                return df
            except BaseException as e:
                continue
        raise ValueError(f"ファイル {filename} を読み込むことができませんでした。")

    def address_width_count(self, text):
        count = 0
        for c in text:
            if unicodedata.east_asian_width(c) in 'FWA':
                count += 1
            else:
                count += 0.5
        return count
    
    def address_check(self, shipcity, shipadd1, shipadd2):
        shipadd1 = '' if pd.isna(shipadd1) else shipadd1
        shipadd2 = '' if pd.isna(shipadd2) else shipadd2
        # 住所の長さをチェックして適切に分割する関数
        A1 = self.address_width_count(shipcity + shipadd1)
        A2 = self.address_width_count(shipadd2)
        if A1 <= 16 and A2 <= 16:
            return shipcity + shipadd1, shipadd2

        A1 = self.address_width_count(shipcity)
        A2 = self.address_width_count(shipadd1 + shipadd2)
        if A1 <= 16 and A2 <= 16:
            return shipcity, shipadd1 + shipadd2

        fullAddress = shipcity + shipadd1 + shipadd2
        idx = int(len(fullAddress) / 2)

        return fullAddress[:idx], fullAddress[idx:]
    
    def data_setter(self) -> None:
        files = os.listdir(os.environ['PASS1'])
        main_files = [f for f in files if 'autoprice' not in f]
        sub_files = [f for f in files if 'autoprice' in f]

        for filename in sub_files:
            customerDf = self.fileReader(filename)

            
        for filename in main_files:
            customerDf = self.fileReader(filename)
            customerDf['Id'] = customerDf['Id']

            customerDf['zip1'] = customerDf['ShipZipCode'].str[:3]
            customerDf['zip2'] = customerDf['ShipZipCode'].str[3:]

            customerDf['name'] = customerDf['ShipLastName'] + customerDf['ShipFirstName']
            address_checked = customerDf.apply(
                lambda row: self.address_check(row['ShipCity'], row['ShipAddress1'], row['ShipAddress2']), axis=1)
            customerDf[['add1', 'add2']] = pd.DataFrame(address_checked.tolist(), index=customerDf.index)

            customerDf['gift'] = [[False, 0]]
            # customerDf['phone'] = customerDf['ShipPhoneNumber']
            customerDf['price_list'] = customerDf['UnitPrice'].str.split('&').apply(
                lambda prices: [str(int(p.split('=')[1]) + int(customerDf['ShipCharge'].iloc[0]) // len(prices)) for p in prices])

            customerDf['codes'] = customerDf['ItemId'].str.split('&').apply(
                lambda codes: [c.split('=')[1] for c in codes])

            customerDf['q'] = customerDf['QuantityDetail'].str.split('&').apply(
                lambda quantities: [int(q.split('=')[1]) for q in quantities])


            selected_columns = ['Id', 'zip1', 'zip2', 'name', 'ShipPrefecture', 'add1', 'add2', 'ShipPhoneNumber', 'gift', 'codes', 'q', 'price_list']
            customerDf = customerDf[selected_columns]
            customerDf.columns = ['Id', 'zip1', 'zip2', 'name', 'add0', 'add1', 'add2', 'phone', 'gift', 'codes', 'q', 'p_list']
            # self.customer に追加
            self.customer = pd.concat([self.customer, customerDf], ignore_index=True)


    def save_result(self):
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
