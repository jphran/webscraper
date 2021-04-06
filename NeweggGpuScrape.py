import datetime
import re
import logging
import pandas as pd
import time

from webscraper import scraper
from webscraper import slack_messenger

# logging setup
logging.basicConfig(filename='/tmp/NeweggGpuScrape.log', filemode='w',
                    level=logging.INFO, format='%(asctime)s - %(levelname)s: '
                                               '%(message)s')

# acceptable purchase params
MIN_PRICE = 200
MAX_PRICE = 500
PRICE_COL = 'price-current'
STOCK_COL = 'item-promo'
DESCRIPTION_COL = 'item-title'
OUT_OF_STOCK = 'OUT OF STOCK'
# must be used against a lower case string
APPROVED_LIST = [
    r'rx\s*5700',
    r'rtx\s*2080',
    r'rtx\s*3060\s*ti',
    r'rtx\s*3070',
    r'rx\s*6800',
    r'rx\s*6900\s*xt',
    r'rtx\s*3080',
    r'radeon\s*vii',
    r'rtx\s*3090',
    # not wanted, but will take
    r'1080\s*ti',
    r'rx\s*6700\s*xt',
    # testing only
    r'1060'
]

approved_list = r'|'.join(APPROVED_LIST)

# html objects to pull from item container
items_of_interest = {
            'a': {'class': 'item-title'},
            'li': {'class': 'price-current'},
            'p': {'class': 'item-promo'}  # out of stock indicator
        }

# create a slack messenger
messenger = slack_messenger.SlackMessenger()

if __name__ == '__main__':
    # create csv
    file_name = '/tmp/gpu_inventory_' \
                + datetime.datetime.now().strftime('%x_%X') \
                    .replace('/', '_').replace(':', '_') + '.csv'

    with open(file_name, 'w') as file:
        # csv headers
        headers = ''
        for i in items_of_interest.values():
            headers += i["class"] + ','

        file.write(headers + '\n')

        # TODO: should use dynamic programming, but f scalping
        page_search_limit = 30  # this is to reduce time and avoid errs
        for n in range(1, page_search_limit+1):
            try:
                gpu_page = scraper.PageScraper(
                    'https://www.newegg.com/Desktop-Graphics-Cards'
                    '/SubCategory/ID-48/Page-' + str(n)
                    + '?Tid=7709&recaptcha=pass')
            except FileNotFoundError as err:
                logging.warning(f'')

            component_type = "div"
            component = {"class": "item-container"}
            gpu_page.get_all_containers(component_type, component)

            csv_input = gpu_page.search_containers_for(items_of_interest)
            file.write(csv_input)

    df = pd.read_csv(file_name)

    # find me a gpu
    for idx, gpu_price in enumerate(df[PRICE_COL]):
        try:
            price = re.search(r'\$[1-9]\d*.\d*', gpu_price).group(0)[1:]
            df.at[idx, PRICE_COL] = price
            price_float = float(price)
            try:
                if MIN_PRICE < price_float < MAX_PRICE \
                        and df.loc[idx][STOCK_COL] != OUT_OF_STOCK:
                    if re.search(approved_list, df.loc[idx][DESCRIPTION_COL]):
                        messenger.send_message(df.loc[idx])
                        logging.info(f"Messenger said, '{df.loc[idx]}'")
                    else:
                        logging.info(f"GPU not pre-approved at {idx}")
            except TypeError as err:
                logging.warning(f"Failed to regex search for descript on gpu "
                                f"at {idx}: {err.args}")
        except TypeError as err:
            logging.warning(f"Failed to regex search for price on gpu at {idx}"
                            f": {err.args}")

