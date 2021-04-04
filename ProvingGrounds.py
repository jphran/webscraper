import re
import pandas as pd
import math

if __name__ == "__main__":
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
        r'rx\s*6700\s*xt'
    ]

    df = pd.read_csv('/tmp/gpu_inventory_04_04_21_15_03_01.csv')
    min_price = 200
    max_price = 500
    approved_list = r'|'.join(APPROVED_LIST)

    for idx, gpu_price in enumerate(df[PRICE_COL]):
        try:
            price = re.search(r'\$[1-9]\d*.\d*', gpu_price).group(0)[1:]
            df.at[idx, PRICE_COL] = price
            price_float = float(price)
            try:
                if min_price < price_float < max_price \
                        and df.loc[idx][STOCK_COL] != OUT_OF_STOCK:
                    if re.search(approved_list, df.loc[idx][DESCRIPTION_COL]):
                        print(df.loc[idx])
                    else:
                        print(f"GPU not pre-approved at {idx}")
            except TypeError as err:
                print(f"Failed to regex search for descript on gpu at "
                      f"{idx}: {err.args}")
        except TypeError as err:
            print(f"Failed to regex search for price on gpu at {idx}: "
                  f"{err.args}")
