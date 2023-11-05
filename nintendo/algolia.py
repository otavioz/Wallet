import consts as CONS
import requests
import json
import xmltodict
from handlers.execeptions import AlgoliaAPIError
from nintendo.game import Game,AlgoliaGameUS
import re

#https://gist.github.com/Shy07/822eff655ec8da2717f269bc21c65976?permalink_comment_id=3744881#%E6%B8%B8%E6%88%8F%E4%BB%B7%E6%A0%BC%E6%9F%A5%E8%AF%A2-game-price-query
DIRECTORY = 'db/usgames.json'
ALG_PARAMS = "filters=&hitsPerPage=100&page={npage}&analytics=true&facetingAfterDistinct=true&clickAnalytics=true&highlightPreTag=%5E*%5E%5E&highlightPostTag=%5E*&attributesToHighlight=%5B%22description%22%5D&facets=%5B%22*%22%5D&maxValuesPerFacet=100"

class AlgoliaAPI():

    def search_game(self,game_name,full=False):
        all_games = self.__us_search_game(game_name)
        #Em US e EU é procurado pelo Nome digitado, porém na Asia (Japão) é procurado pelo Product Code devido ao uso de ideogramas japoneses no título
        if not full:
            for i,game in enumerate(all_games):
                all_games[i] = self.__eu_search_game(game,game_name)
                all_games[i] = self.__jp_search_game(game)
        else:
            all_games.extend(self.__eu_search_game(game,game_name))
            all_games.extend(self.__jp_search_game(game))
        return all_games

    def get_game_info(self,game_name):
        pass

    def __us_search_game(self,game_name:str):
        games = []
        npage = 0
        url = CONS.ALGOLIA_URL.format(algoliaid = CONS.ALGOLIA_ID)
        payload = {
            "requests": [
                {
                    "indexName": "store_game_en_us",
                    "query": game_name,
                    "params": ALG_PARAMS.format(npage=npage)
                }
            ]
        }

        headers = {'X-Algolia-Application-Id': CONS.ALGOLIA_ID,
            'X-Algolia-API-Key': CONS.ALGOLIA_API_KEY,
            'User-Agent': 'Algolia for JavaScript (4.19.0); Browser'}

        r = requests.post(url, data=json.dumps(payload), headers=headers)
        if r.status_code != 200:
            raise AlgoliaAPIError(r.status_code)
        while len(r.json()['results'][0]['hits']) > 0: #r.json()['results'][0]['nbHits'] > 0:
            for item in r.json()['results'][0]['hits']:
                if re.sub('[^A-Za-z0-9 ]+', '', game_name.lower()) in re.sub('[^A-Za-z0-9 ]+', '', item["title"].lower()):
                    games.append(AlgoliaGameUS(item))
            npage += 1
            payload['requests'][0]['params'] = ALG_PARAMS.format(npage=npage)
            r = requests.post(url, data=json.dumps(payload), headers=headers)
        return games
    
    def __eu_search_game(self,game:Game,game_name):
        url = CONS.NINTENDO_EU_URL
        params = {'q': game_name, 'wt': 'json', 'sort': 'title asc', 'start': 0, 'rows': 200, 'fq': 'type:GAME AND system_names_txt:"Switch"'}
        response = requests.get(url, params=params)
        docs = response.json().get('response').get('docs', [])
        while response.status_code == 200 and len(docs) > 0:
            for item in docs:
                    if re.sub('[^A-Za-z0-9 ]+', '', game.name.lower()) in re.sub('[^A-Za-z0-9 ]+', '', item["title"].lower()):
                        game.nsuids['EU'] = item["nsuid_txt"][0]
                        game.product_code = item['product_code_txt'][0] if 'product_code_txt' in item else 0
            params['start'] += 200
            response = requests.get(url, params=params)
            docs = response.json().get('response').get('docs', [])
        return game

    def __jp_search_game(self,game:Game):
        url = CONS.NINTENDO_JP_URL
        response = requests.get(url)
        xml = xmltodict.parse(response.text)['TitleInfoList']['TitleInfo']
        if response.status_code == 200 and game.product_code != '0':
            for data in xml:
                if game.product_code in data["InitialCode"]:
                    game.nsuids['JP'] = data["LinkURL"].split("/")[-1]
        return game