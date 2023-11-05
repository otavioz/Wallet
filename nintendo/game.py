class Game():

    def __init__(self,name='',
                 product_code=0,
                 nsuid=0,
                 origin='US',
                 game_thumb='',
                 availability=False,
                 price_list={},
                 br_price_list={}) -> None:
        
        self.name = name
        self.product_code = product_code
        self.nsuids = {'US':0,'EU':0,'JP':0} #Also named title_id
        self.nsuids[origin] = nsuid
        self.game_thumb = game_thumb
        self.availability = availability
        self.price_list = price_list
        self.br_price_list = br_price_list

    def save_game(self) -> None:
        pass

    def add_price(self,price,region,currency,on_sale,discount_price=0,start_date=None,end_date=None,brl=False):
        best_price = discount_price if on_sale else price
        nd_price = price if on_sale else discount_price
        if not brl:
            self.price_list.update({currency:{'price':best_price,
                                            'nd_price':nd_price,
                                            'region':region,
                                            'on_sale':on_sale,
                                            'start_date':start_date,
                                            'end_date':end_date}})
        else:
            self.br_price_list.update({currency:{'price':best_price,
                                            'nd_price':nd_price,
                                            'region':region,
                                            'on_sale':on_sale,
                                            'start_date':start_date,
                                            'end_date':end_date}})
    def add_nsuid(self,id,origin):
        self.nsuids[origin] = id
    
    def all_nsuids(self):
        return []

    @property
    def product_code(self):
        return self.__product_code
    
    @product_code.setter
    def product_code(self, var):
        '''
        HACPAAB6B (NA)
        HACPAAB6C (EU)
         HACAAB6A (JP)
        JUST DANCE EU: HACYA8FZQ JP: HACA8FZA
        '''
        var = str(var)
        if var[0:3] == 'HAC':
            self.__product_code = var[-5:][:4]
        else:
            self.__product_code = '0'

    def get_best_prices(self):
        return dict(sorted(self.br_price_list.items(), key=lambda x:x[1]['price']))

    def __str__(self) -> str:
        return f'{self.name}, {self.product_code}, {self.nsuids}, {self.price_list}, {self.br_price_list}'
    
class AlgoliaGameUS(Game):
    def __init__(self,jsn) -> None:
        super().__init__(
            name = jsn['title'],
            nsuid = jsn['nsuid'],
            origin = 'US',
            game_thumb = jsn['productImage'])
    