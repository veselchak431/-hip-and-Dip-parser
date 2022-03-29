import bs4
import requests
import pandas as pd
import numpy as np


def get_list_of_correct_products_on_page(elements):
    list_of_products_on_page = np.array([['name', 'src', 'price', 'voltage', 'current', 'power'], ])
    for element in elements:

        datalist = element.find("div", attrs={"class": "pps"}).findAll("div")

        if datalist[0].find("span", attrs={"class": "item__avail item__avail_available nw"}):
            price = element.find('span', attrs={"class": "price"}).contents[0].contents[0]
            face = element.find("a", attrs={"class": "link"})
            src = face['href']
            name = face.contents[0]
            voltage_V = "-"
            current_I = "-"
            power_W = "-"
            for d in datalist:

                if 'Максимальное напряжение сток-исток Uси,В: ' in d.contents:
                    voltage_V = d.find('span').contents[0]
                if 'Сопротивление канала в открытом состоянии Rси вкл. (Max) при Id, Rds (on): ' in d.contents:
                    current_I = d.find('span').contents[0]
                    current_I = current_I[0:current_I.find('Ом')].replace('.', ',')
                if 'Максимальная рассеиваемая мощность Pси макс..Вт: ' in d.contents:
                    power_W = d.find('span').contents[0]
                    power_W = power_W.replace('.', ',')

            if voltage_V != "-" and current_I != "-" and power_W != "-":
                new_list = np.array([name, src, price, voltage_V, current_I, power_W])
                list_of_products_on_page = np.vstack([list_of_products_on_page, new_list])

    list_of_products_on_page = list_of_products_on_page[1:]
    return list_of_products_on_page


if __name__ == '__main__':
    list_of_products = np.array([['name', 'src', 'price', 'voltage', 'current', 'power'], ])
    page = 1
    while True:
        print('page', page)
        res = requests.get(f"https://www.chipdip.ru/catalog/field-effect-transistor?sort=priceup&ps=x3&page={page}")
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        elements = soup.findAll(attrs={"class": "with-hover"})
        if soup.find(attrs={"class": "link no-visited pager__control pager__next"}):
            list_of_products = list_of_products_on_page = np.vstack([list_of_products,
                                                                     get_list_of_correct_products_on_page(elements)])
            page += 1
        else:
            break

    list_of_products = list_of_products[1:]
    df = pd.DataFrame(list_of_products,
                       columns=['name', 'src', 'price', 'voltage', 'current', 'power'])
    print(df)
    df.to_excel('./Chip_i_dip.xlsx', sheet_name='Budgets', index=False)
