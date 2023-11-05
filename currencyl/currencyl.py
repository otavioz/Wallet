
from datetime import datetime
import json
import logging
import requests
import consts as CONST
import os

DIRECTORY = 'db/currencylayer.json'
class Currencyl():

    def get_currencies(self,online=False):
        if online:
            params = {"access_key":os.getenv('currencyl_apy_key'),
                      "currencies":','.join(CONST.CURRENCIES),
                      "format":1}
            r = requests.get(CONST.URL_CURRENCYL,params=params)
            if r.status_code not in range(200, 299):
                logging.warning(f' Erro na chamada API Currency Layer: {str(r.status_code)} {r.text}')
                return self.__get_currencies()
            self.__save_currencies(r.text)
            return r.text
        else:
            return self.__get_currencies()

    def __save_currencies(self,json_string):
        with open(DIRECTORY,'w') as outfile:
            outfile.write(json_string)

    def __get_currencies(self):
        with open(DIRECTORY,'r') as outfile:
            return json.load(outfile)