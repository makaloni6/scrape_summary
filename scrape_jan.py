import pandas
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import csv


def make_url(code):
    return os.environ['TEMP_URL'].format(code)


def scrapeJan(url):
    res = requests.get(url)
    print(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    

def main():

    load_dotenv()

    with open(os.environ['FILENAME']) as f:
        reader = csv.reader(f)
        rows = [row[0] for row in reader]

    for code in rows[:1]:
        url = make_url(code)
        scrapeJan()

if __name__ == '__main__':
    main()