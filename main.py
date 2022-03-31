import bs4
import requests
import pandas as pd
import re


class ChipParser:
    """class that parses the chip and dip website url and returns a data frame or excel file with the characteristics
    of the available products """


    _url = ''
    _search_properties = []
    _data = pd.DataFrame()

    def __init__(self, url):
        """method validate url, remove unnecessary and save it"""
        if self._is_url_chip_and_dip_catalog(url):
            self._url = self._made_cleaned_chip_and_dip_url(url)
        else:
            print("некорректный url")

    def set_search_properties(self, list_of_properties):
        """method accept, validate and save properties"""
        for properties in list_of_properties:
            if properties in self.get_list_of_properties():
                self._search_properties.append(properties)
            else:
                print('неизвестная категория')

    def get_list_of_properties(self):
        """method return available properties from url"""
        list_of_properties = []
        response = requests.get(self._url)
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        properties = soup.findAll('div', attrs={"class": "filter_name filter_opener"})
        for p in properties:
            list_of_properties.append(p.contents[0])
        list_of_properties.remove('Наличие в магазинах')
        return list_of_properties

    def _get_dataframe_of_correct_products_on_page(self, url):
        """method return dataframe of products in stock with their properties, saved in the class"""
        response = requests.get(url)
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        products = soup.findAll(attrs={"class": "with-hover"})

        dataframe_of_products_on_page = pd.DataFrame()

        for product in products:

            datalist = product.find("div", attrs={"class": "pps"}).findAll("div")

            if datalist[0].find("span", attrs={"class": "item__avail item__avail_available nw"}):

                price = product.find(id=re.compile("^price")).contents[0]
                src = product.find("a", attrs={"class": "link"})['href']
                name = product.find("a", attrs={"class": "link"}).contents[0]
                production = datalist[1].find('span', attrs={"class": "itemlist_pval"}).contents[0]

                dict_of_product_with_properties = dict.fromkeys(self._search_properties)
                dict_of_product_with_properties['Бренд / Производитель'] = production

                for d in datalist:

                    for key in dict_of_product_with_properties.keys():

                        if key + ": " in d.contents:
                            dict_of_product_with_properties[key] = d.find('span').contents[0]

                dict_of_product = {'Название': name,
                                   'Ссылка': src
                                   }
                dict_of_product.update(dict_of_product_with_properties)
                dict_of_product.update({'Цена': price})

                dataframe_of_product = pd.DataFrame(dict_of_product, index=[0])

                if len(dataframe_of_products_on_page) == 0:
                    dataframe_of_products_on_page = dataframe_of_product
                else:
                    dataframe_of_products_on_page = pd.concat([dataframe_of_products_on_page, dataframe_of_product])

        return dataframe_of_products_on_page

    def create_dataframe_of_products(self):
        """pass all pages and save dataframe with data of all pages"""
        page = 1
        while True:
            print('page', page)

            data_of_page = self._get_dataframe_of_correct_products_on_page(f"{self._url}?ps=x3&page={page}")

            res = requests.get(f"{self._url}?ps=x3&page={page}")
            soup = bs4.BeautifulSoup(res.text, 'html.parser')

            if soup.find(attrs={"class": "link no-visited pager__control pager__next"}):
                if len(self._data) == 0:
                    self._data = data_of_page
                else:
                    self._data = pd.concat([data_of_page, self._data])
                page += 1
            else:
                break

    def _is_url_chip_and_dip_catalog(self, url):
        """validate url"""
        try:
            url_list = url.split('/')
            is_url_chip_and_dip = url_list[2] == 'www.chipdip.ru'
            is_page_category = url_list[3] in ('catalog', 'catalog-show')

            if is_url_chip_and_dip and is_page_category:
                response = requests.get(url)
                soup = bs4.BeautifulSoup(response.text, 'html.parser')
                if soup.find('div', attrs={"class": "no-visited filter__sorts"}):
                    return True

            return False
        except:
            return False

    def _made_cleaned_chip_and_dip_url(self, url):
        """remove unnecessary parameters from url"""
        url_list = url.split('/')
        if url_list[3] == 'catalog-show':
            url_list[3] = 'catalog'
        category = url_list[4]
        if category.find('?') != -1:
            category = category[0:category.find('?')]
            url_list[4] = category
        url = '/'.join(url_list)
        return url

    def get_dataframe(self):
        """return dataframe"""
        return self._data

    def create_and_export_dataframe_as_exel(self, path):
        """create dataframe if it is empty, and save it on path"""
        if len(self._data) == 0:
            self.create_dataframe_of_products()
        try:
            self._data.to_excel('./Chip_i_dip.xlsx', sheet_name='sheet1', index=False)#переделать
        except:
            print("неверный путь или ошибка сохранения")


if __name__ == '__main__':
    url = "https://www.chipdip.ru/catalog/round-leds"

    parser = ChipParser(url)
    list = parser.get_list_of_properties()
    parser.set_search_properties(list)
    parser.create_dataframe_of_products()
    print(parser.get_dataframe())
    parser.create_and_export_dataframe_as_exel('asd')

