import requests
import json
import xmltodict
from currencyl.currencyl import Currencyl
from handlers.execeptions import PriceAPIError
from nintendo.game import Game,AlgoliaGameUS
import re
import consts as CONS

class PriceAPI:

    def get_prices(game:Game) -> Game:
    #try:
        headers = {'Content-Type': 'application/json'}
        currency_values = Currencyl().get_currencies()
        for region,countries in CONS.ESHOPS.items():
            for _,acronym in countries.items():
                params={"country":acronym,"ids":str(game.nsuids[region]),"lang":"en","limit":"50"}
                response = json.loads(requests.get(CONS.PRICE_API_URL,headers=headers,params=params).text)
                if response != []:
                    if len(response['prices']) > 0:
                        price = response['prices'][0]
                        discounted = True if len(response['prices']) > 1 else False
                        if price['sales_status'] != 'not_found': #What we want is onsale
                            if 'regular_price' in price:
                                game.add_price(price['regular_price']['raw_value'],
                                            region,
                                            price['regular_price']['currency'],
                                            discounted,
                                            price['discount_price']['raw_value'] if discounted else 0,
                                            price['discount_price']['start_datetime'] if discounted else None,
                                            price['discount_price']['end_datetime'] if discounted else None)               
                                tax = currency_values['quotes'][f'USD{price["regular_price"]["currency"]}'] if price["regular_price"]["currency"] != 'USD' else 1
                                game.add_price(float(price['regular_price']['raw_value']) / tax * currency_values['quotes']['USDBRL'],
                                            region,
                                            price['regular_price']['currency'],
                                            discounted,
                                            float(price['discount_price']['raw_value']) / tax * currency_values['quotes']['USDBRL'] if discounted else 0,
                                            price['discount_price']['start_datetime'] if discounted else None,
                                            price['discount_price']['end_datetime'] if discounted else None,
                                            brl=True)
                            
        return game
    #except KeyError as e :
    #    raise PriceAPIError(e)
    #except Exception as e:
    #    raise e
    #finally:
    #    return game