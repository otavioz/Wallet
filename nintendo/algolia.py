import consts as CONS
import requests
import json
#import xmltodict
from db.db import DataBase
import re

class AlgoliaAPI():

    def __init__(self) -> None:
        self.directory = 'db/usgames.json'

    def __save_json(self,json_string):
        with open(self.directory,'w') as outfile:
            outfile.write(json_string)

    def search_game(self,game_name,online=False):
        all_games = self.__us_search_game(game_name)
        #self.__save_json(all_games)
        #Em US e EU é procurado pelo Nome digitado, porém na Asia (Japão) é procurado pelo Product Code devido ao uso de ideogramas japoneses no título
        #for n,game in enumerate(all_games):
        #    all_games[n] = __eu_search_game(game)
        #    
        #for n,game in enumerate(all_games):
        #    all_games[n] = __jp_search_game(game)

        return all_games

    def __us_search_game(self,game_name:str):
        games = []
        url = CONS.ALGOLIA_URL.format(algoliaid = CONS.ALGOLIA_ID)
        payload = {'query': 70010000000,
            'allowTyposOnNumericTokens': False,
            'queryType': 'prefixAll',
            'restrictSearchableAttributes': ['nsuid'],
            'facetFilters': ['platform:Nintendo Switch'],
                'hitsPerPage': 500}

        headers = {'X-Algolia-Application-Id': CONS.ALGOLIA_ID,
            'X-Algolia-API-Key': CONS.ALGOLIA_API_KEY,
            'User-Agent': 'Algolia for Python (2.4.0); Python (3.8.3)',
            'Content-Type': 'application/json'}

        r = requests.post(url, data=json.dumps(payload), headers=headers)
        with open(self.directory,'w',encoding="utf-8") as outfile:
           json.dump(r.text, outfile, ensure_ascii=False)
        #while r.json()['nbHits'] > 0:
        #    for item in r.json()['hits']:
        #        if re.sub('[^A-Za-z0-9 ]+', '', game_name.lower()) in re.sub('[^A-Za-z0-9 ]+', '', item["title"].lower()):
        #            games.append(Game.Game(item["title"],{"US":item["nsuid"]}))
        #    payload['query'] += 1
        #    r = requests.post(url, data=json.dumps(payload), headers=headers)
        return games

    #def __eu_search_game(self,game_name):
    #    url = CONS.NINTENDO_EU_URL
    #    params = {'q': '*', 'wt': 'json', 'sort': 'title asc', 'start': 0, 'rows': 200, 'fq': 'type:GAME AND system_names_txt:"Switch"'}
    #    response = requests.get(url, params=params)
    #    json = response.json().get('response').get('docs', [])
    #    while response.status_code == 200 and len(json) > 0:
    #        for item in json:
    #                if re.sub('[^A-Za-z0-9 ]+', '', game.get_title().lower()) in re.sub('[^A-Za-z0-9 ]+', '', item["title"].lower()):
    #                    #games.append(Game.Game(item["title"],{"EU":item["nsuid_txt"][0]},item['product_code_txt'][0]))                    
    #                    game.set_nsuids({"EU":item["nsuid_txt"][0]})
    #                    game.set_product_code(item['product_code_txt'][0])  
    #                    game.set_img_url(item['image_url_sq_s'])                 
    #        params['start'] += 200
    #        response = requests.get(url, params=params)
    #        json = response.json().get('response').get('docs', [])
    #    return game
#
    #def __jp_search_game(self,game:Game):
    #    url = f"https://www.nintendo.co.jp/data/software/xml/switch.xml"
    #    response = requests.get(url)
    #    xml = xmltodict.parse(response.text)['TitleInfoList']['TitleInfo']
    #    if response.status_code == 200:
    #        for data in xml:
    #            if game.to_jp_product_code() == data["InitialCode"]:
    #                #result.append(f'\n{data["TitleName"]}:{data["LinkURL"].split("/")[-1]}:{data["InitialCode"]}')
    #                game.set_nsuids({"JP":data["LinkURL"].split("/")[-1]})
    #    return game
#
    #def __call_api_price(self, nsuids):
    #    prices = []
    #    for region,nsuid in nsuids.items():   
    #        headers = {'Content-Type': 'application/json'}        
    #        for _,acronym in CONS.ESHOPS[region].items():
    #            params={"country":acronym,"ids":str(nsuid),"lang":"en","limit":"50"}
    #            response = json.loads(requests.get(CONS.PRICE_GET_URL,headers=headers,params=params).text)
    #            if response != []:
    #                p = Price.Price(response)
    #                if p.onSale:
    #                    brl_value = Currency.convert_to_brl(p.currency,p.raw_value)
    #                    brl_salve_value = Currency.convert_to_brl(p.currency,p.raw_saleValue) if p.raw_saleValue != 0 else 0
    #                    p.set_brl_price(Currency.calculate_iof(p.currency,brl_value),Currency.calculate_iof(p.currency,brl_salve_value))
    #                    prices.append(p)
    #            else:
    #                #TODO Gravar LOG contendo erro
    #                pass
    #    return prices