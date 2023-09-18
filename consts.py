#GOOGLE SHEETS
GOOGLE_SHEETS_SCOPES =  ['https://www.googleapis.com/auth/spreadsheets']

#NUBANK
MONTHS = ['All','Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro','Janeiro']

#DB
DB_FILE_NAME = "db/db.cfg"
CSVNUAFILE = 'files/nuaccount.csv'

#API KEY CURRENCY LAYER FREE PLAN
URL_CURRENCYL = "http://api.currencylayer.com/live"
CURRENCIES = ["BRL","CAD","MXN","COP","ARS","CLP","PEN","CZK","DKK","EUR","ILS","NOK","PLN","RUB","ZAR","SEK","GBP","JPY","KRW","TWD","HKD","AUD","NZD"]


#ESHOPS PER REGION
ESHOPS = {"US":{"USA":"US","Canada":"CA","Mexico":"MX","Brasil":"BR","Colombia":"CO","Argentina":"AR","Chile":"CL","Peru":"PE"},
    "EU":{"Austria":"AT","Belgie":"BE","Czech Republic":"CZ","Denmark":"DK","Deutschland":"DE","España":"ES","Finland":"FI","France":"FR","Greece":"GR","Hungary":"HU","Israel":"IL","Italia":"IT","Nederland":"NL","Norway":"NO","Slovakia":"SK","Poland":"PL","Portugal":"PT","Russia":"RU","South Africa":"ZA","Sweden":"SE","UK & Ireland":"GB"},
    "JP":{"Japan":"JP","Korea":"KR","China Mainland":"CH","Hong Kong":"HK","Australia":"AU","New Zealand":"NZ"}}

LOCALES = {"US":"USA","CA":"Canada","MX":"Mexico","BR":"Brasil","CO":"Colombia","AR":"Argentina","CL":"Chile","PE":"Peru","AT":"Austria","BE":"Belgie","CZ":"Czech Republic","DK":"Denmark","DE":"Deutschland","ES":"España","FI":"Finland","FR":"France","GR":"Greece","HU":"Hungary","IL":"Israel","IT":"Italia","NL":"Nederland","NO":"Norway","SK":"Slovakia","PL":"Poland","PT":"Portugal","RU":"Russia","ZA":"South Africa","SE":"Sweden","GB":"UK & Ireland","JP":"Japan","KR":"Korea","CH":"China Mainland","HK":"Hong Kong","AU":"Australia","NZ":"New Zealand",
}

#ALGOLIA URL TO GET GAMES US
ALGOLIA_URL = 'https://{algoliaid}-dsn.algolia.net/1/indexes/ncom_game_en_us/query'
#ALGOLIA API KEY to use on request header
ALGOLIA_API_KEY = 'c4da8be7fd29f0f5bfa42920b0a99dc7'
#ALGOLIA ID on URL
ALGOLIA_ID = 'U3B6GR4UA3'
#FOR TESTS
SAMPLE_US_GAME_NSUID = 70010000027619
SAMPLE_GAME_NAME = 'Animal Crossing'

#URL LINK TO EU GAMES
NINTENDO_EU_URL ='https://search.nintendo-europe.com/en/select'

#NINTENDO PRICE API
PRICE_API_URL = "https://api.ec.nintendo.com/v1/price"