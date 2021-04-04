import datetime
import re
import pandas as pd

from webscraper import scraper

if __name__ == '__main__':
    # create csv
    file_name = '/tmp/gpu_inventory_' \
                + datetime.datetime.now().strftime('%x_%X') \
                    .replace('/', '_').replace(':', '_') + '.csv'
    with open(file_name, 'w') as file:
        items_of_interest = {
            'a': {'class': 'item-title'},
            'li': {'class': 'price-current'},
            'p': {'class': 'item-promo'}  # out of stock indicator
        }

        headers = ''
        for i in items_of_interest.values():
            headers += i["class"] + ','
        file.write(headers + '\n')

        for n in range(1, 89):
            gpu_page = scraper.PageScraper(
                'https://www.newegg.com/Desktop-Graphics-Cards'
                '/SubCategory/ID-48/Page-' + str(n) + '?Tid=7709')

            component_type = "div"
            component = {"class": "item-container"}
            gpu_page.get_all_containers(component_type, component)

            csv_input = gpu_page.search_containers_for(items_of_interest)
            file.write(csv_input)

    # find me a gpu
    df = pd.read_csv(file_name)
    min_price = 200
    max_price = 500

    for idx, gpu_price in enumerate(df['price-current']):
        price = re.search(r'\$[1-9]\d*.\d*', gpu_price).group(0)[1:]

        if min_price < float(price) < max_price:
            print(df[idx])
