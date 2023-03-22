import copy
from datetime import datetime
import json
from dateutil.relativedelta import relativedelta
from finances.model import DebtModel
import consts as CONST
from db.db import DataBase
import logging

#TODO Analise do VALOR deeve sempre vir primeiro que a CATEGORIA

DICTIONARY = {
        'Cartão Físico': ['card_present'],
        'Cartão Virtual': ['card_not_present'],
        '':['None']}

class Debt:
    def __init__(self,**kwargs):
        self.payment_charges = []
        self.title = kwargs.get('title')
        self.origin = kwargs.get('origin')
        self.amount = kwargs.get('amount')
        self.category = kwargs.get('category')
        self.timedate = kwargs.get('timedate')
        self.ref_month = kwargs.get('ref_month')
        self.details = kwargs.get('details')
        self.debtor = kwargs.get('debtor') if 'debtor' in kwargs else ''
        self.created_date = kwargs.get('created_date') if 'created_date' in kwargs else datetime.now()
        self.__update_values()
    
    def __str__(self):
        return """
            Title: {}
            Origin: {}
            Amount: {}
            Category: {}
            Date: {}
            Reference: {}
            Details: {}
            Debtor: {}
            Created Date: {}
            """.format(self.title,self.origin,self.amount,self.category,self.timedate,self.ref_month,self.details,self.debtor,self.created_date)

    def to_list(self):
        return [
            self.title,
            self.origin,
            self.amount,
            self.category,
            self.timedate.strftime("%d/%m/%Y %H:%M:%S"),
            CONST.MONTHS[self.ref_month.month],
            self.details,
            self.debtor,
            self.created_date.strftime("%d/%m/%Y %H:%M:%S"),
        ]
    def __update_values(self):
        origins = DataBase.read_debts_domain('origins')
        if self.origin not in origins:
            origins.append(self.origin)
            DataBase.write_debts_domain('origins',origins)
            #TODO GSheets().append([cat],GS.Categories.table)
            logging.info(f'{datetime.now()} - New ORIGIN domain inserted: {self.origin}')

        categories = DataBase.read_debts_domain('categories')
        if self.category not in categories:
            categories.update({self.category:[]})
            DataBase.write_debts_domain('categories',json.dumps(categories))
            #TODO GSheets().append([cat],GS.Categories.table)
            logging.info(f'{datetime.now()} - New CATEGORY domain inserted: {self.category}')

    def get_payment_charges(self):
        return self.payment_charges

    def __add_payment_charges(self):
        """
        Overwrited by child classes.
        """
        pass

    @staticmethod
    def get_closing_day():
        return DataBase.read_debts_domain("closing_day")

    def __get_refmonth(datetime_):
        """
        Overwrited by child classes.
        """
        pass

    @staticmethod
    def debtor_list():
        return DataBase.read_debts_domain("debtors")

    @staticmethod
    def origin_list():
        list_o = {}
        for o in DataBase.read_debts_domain('origins'):
            list_o.update({o:0})
        return list_o
    
    @staticmethod
    def category_list():
        list_c = {}
        for o in DataBase.read_debts_domain('categories').keys():
            list_c.update({o:0})
        return list_c
        
    
class NubankDebt(Debt):

    def __init__(self,jsn) -> None:
        self.count = 0
        super().__init__(
                title= jsn['description'],
                origin= "Nubank",
                amount= self.__getamount(jsn),
                category= jsn['title'],
                timedate= datetime.strptime(jsn['time'],"%Y-%m-%dT%H:%M:%SZ"),
                ref_month= self.__get_refmonth(jsn['time']),
                details=self.__get_details(jsn['details']))
        self.__add_payment_charges()

    def __get_refmonth(self,datetime_):
        closing_day = Debt.get_closing_day()
        ref_month = datetime.strptime(datetime_,"%Y-%m-%dT%H:%M:%SZ")
        if ref_month.day >= closing_day:
            ref_month = ref_month + relativedelta(months=1)
        return ref_month
    
    def __getamount(self,jsn):
        if 'charges' in jsn['details']:
            self.count = jsn['details']['charges']['count']
            return -int(jsn['details']['charges']['amount'])/100
        return -int(jsn['amount'])/100

    def __get_details(self,input):
        details = []
        if 'subcategory' in input:
            details.extend([key for key,value in DICTIONARY.items() if input['subcategory'] in value])
        return ' | '.join(details)

    def __add_payment_charges(self):
        for c in range(1,self.count):
            copy_input = copy.copy(self)
            copy_input.ref_month = copy_input.ref_month + relativedelta(months=c)
            self.payment_charges.append(copy_input)

class NuAccountDebt(Debt):
    def __init__(self,jsn):
        super().__init__(
                title= jsn['title'],
                origin= "Nuconta",
                amount= self.__getamount(jsn),
                category= 'movimentação',
                timedate= datetime.strptime(jsn['postDate'],"%Y-%m-%d"),
                ref_month= self.__get_refmonth(jsn['postDate']),
                details=self.__get_details(jsn),
                debtor=self.__get_debtor(jsn['detail']))
        self.__add_payment_charges()

    def __get_refmonth(self,datetime_):
        closing_day = Debt.get_closing_day()
        ref_month = datetime.strptime(datetime_,"%Y-%m-%d")
        if ref_month.day >= closing_day:
            ref_month = ref_month + relativedelta(months=1)
        return ref_month
    
    def __getamount(self,jsn):
        if jsn['title'] == 'Pagamento agendado':
            return 0
        if jsn['kind'] == 'POSITIVE' or jsn['title'] == 'Resgate fundo' or jsn['title'] == 'Pagamento devolvido':
            return float(jsn['amount'])
        else:
            return -float(jsn['amount'])
    
    def __get_details(self,input):
        details = []
        if 'tags' in input and input['tags'] is not None:
            details.append('Tags:' + ','.join(input['tags']))
        if 'footer' in input and input['footer'] is not None:
            details.append(str(input['footer']).replace('\n',' '))
        if 'detail' in input and input['detail'] is not None:
            #details.append(str(input['detail']).replace('\n',' '))
            list_ = self.debtor_list()
            for debtor in input['detail'].split('\n'):
                if debtor not in list_:
                    details.append(debtor)
        return ' | '.join(details)

    def __get_debtor(self,input):
        list_ = self.debtor_list()
        for debtor in input.split('\n'):
            if debtor in list_:
                return debtor
        return ''
    
    def __add_payment_charges(self):
        """
        If the debt is an Bill Payment using account values, create an payment to insert on credit card
        """
        if self.title == "Pagamento da fatura":
            self.payment_charges.append(Debt(
                title= self.title,
                origin= "Nubank",
                amount= -self.amount,
                category= 'pagamento',
                timedate= self.timedate,
                ref_month= self.ref_month,
                details= 'Automatic created',
                debtor= '',
            ))

    def get_payment_charges(self):
        return self.payment_charges

class DriveDebt(Debt):
    def __init__(self,jsn):
        model = DebtModel
        super().__init__(
                title= jsn[model.title],
                origin= jsn[model.origin],
                amount= jsn[model.amount],
                category= jsn[model.category],
                timedate= datetime.strptime(jsn[model.timedate],"%d/%m/%Y %H:%M:%S"),
                ref_month= self.__get_refmonth(jsn[model.ref_month]),
                details= jsn[model.details],
                debtor= jsn[model.debtor],
                created_date= datetime.strptime(jsn[model.created_date],"%d/%m/%Y %H:%M:%S"))

    def __get_refmonth(self,input):
        month_num = 1
        for month in CONST.MONTHS:
            if month == input:
                break
            month_num += 1
        return datetime.now().replace(month=month_num)