
from datetime import datetime
import json
import logging
import requests
import consts as CONST
from db.db import DataBase


class Currencyl():

    def __init__(self) -> None:
        self.directory = 'db/currencylayer.json'

    def get_currencies(self,online=False):
        if online:
            params = {"access_key":self.__getapikey(),
                      "currencies":','.join(CONST.CURRENCIES),
                      "format":1}
            r = requests.get(CONST.URL_CURRENCYL,params=params)
            if r.status_code not in range(200, 299):
                #print(f'Endpoint Response Code:{str(r.status_code)} {r.text}\n\nParams: {params}')
                logging.warning(f'{datetime.now()} - Erro na chamada API Currency Layer: {str(r.status_code)} {r.text}')
                return self.__get_currencies()
            self.__save_currencies(r.text)
            return r.text
        else:
            return self.__get_currencies()
        
        
    def __getapikey(self):
        return  DataBase.read_currency_domain('CURRENCYL_API_KEY')

    def __save_currencies(self,json_string):
        with open(self.directory,'w') as outfile:
            outfile.write(json_string)

    def __get_currencies(self):
        with open(self.directory,'r') as outfile:
            return json.load(outfile)