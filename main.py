from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import undetected_chromedriver as uc
import json
from pandas import DataFrame

class AvitoScrapper:
    configs = {
        "site-url": "https://www.avito.ru/",
        "url": "",
        "to-search": "",
        "city": "",
    }

    can_next_page = True
    count_products_to_parse = 30
    data_to_save = []

    def __init__(self, city:str, to_search:str, driver_version:int=None):
        if city and to_search != "":
            self.configs["city"] = city.lower()
            self.configs["to-search"] = "?q=" + to_search.lower().replace(" ", "+")
            self.configs["driver-version"] = driver_version
            self.configs["url"] = f'{self.configs["site-url"]}/{self.configs["city"]}{self.configs["to-search"]}'

    def __set_up(self):
        options = Options()
        options.add_argument("--headless")
        self.driver = uc.Chrome(version_main=self.configs["driver-version"], options=options)

    def __get_url(self):
        self.driver.get(self.configs["url"])

    def __paginator(self):
        while self.driver.find_elements(By.CSS_SELECTOR, "[data-marker='pagination-button/nextPage']"):
            self.__parse_page()
            if self.can_next_page:
                self.driver.find_element(By.CSS_SELECTOR, "[data-marker='pagination-button/nextPage']").click()
            else:
                break

    def __parse_page(self):
        items = self.driver.find_elements(By.CSS_SELECTOR, "[data-marker='item']")
        for item in items:
            if self.count_products_to_parse > 0:
                name = item.find_element(By.CSS_SELECTOR, "[itemprop='name']").text
                price = item.find_element(By.CSS_SELECTOR, "[itemprop='price']").get_attribute("content")
                description = item.find_element(By.CSS_SELECTOR, "[class*='item-description']").text
                link = item.find_element(By.CSS_SELECTOR, "[data-marker='item-title']").get_attribute("href")

                data = {
                    "Название": name,
                    "Цена": price,
                    "Описание": description,
                    "Ссылка": link
                }

                self.data_to_save.append(data)

                self.count_products_to_parse -= 1
                print(f"Осталось товаров - {self.count_products_to_parse} штук")
            else:
                self.can_next_page = False
                break

    def parse(self, count:int=30):
        self.count_products_to_parse = count
        self.__set_up()
        self.__get_url()
        self.__paginator()

    def save_json(self):
        cur_date = datetime.now().strftime("%d_%m_%Y")
        with open(f"{cur_date}_data.json", "w", encoding="utf-8") as json_file:
            json.dump(self.data_to_save, json_file, indent=4, ensure_ascii=False)

    def save_excel(self):
        if self.data_to_save:
            data_excel = {
                "Название": [],
                "Цена": [],
                "Описание": [],
                "Ссылка": []
            }

            for data in self.data_to_save:
                for key, row in data.items():
                    data_excel[key].append(row)

            cur_date = datetime.now().strftime("%d_%m_%Y")
            df = DataFrame(data_excel)
            df.to_excel(f"{cur_date}_data.xlsx", index=False)

def main():
    city = input("Введите ваш город: ")
    to_search = input("Введите запрос: ")

    avito_scrapper = AvitoScrapper(city, to_search)

    try:
        count = int(input("Введите кол-во товара: "))
        avito_scrapper.parse(count)
    except:
        avito_scrapper.parse()

    how_to_save = input("Как вы хотите сохранить (j - json, e - excel, a - all): ")

    if how_to_save == "j":
        avito_scrapper.save_json()
    elif how_to_save == "e":
        avito_scrapper.save_excel()
    elif how_to_save == "a":
        avito_scrapper.save_json()
        avito_scrapper.save_excel()
    else:
        avito_scrapper.save_json()


if __name__ == "__main__":
    main()