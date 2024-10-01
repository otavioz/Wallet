import copy
from datetime import datetime
import json
from dateutil.relativedelta import relativedelta
from finances.model import DebtModel
import consts as CONST
from db.db import DataBase
import logging
import dateutil.parser

#TODO Analise do VALOR deeve sempre vir primeiro que a CATEGORIA

PAYMENT_EVENT_TYPES = (
    'TransferOutEvent',
    'TransferInEvent',
    'TransferOutReversalEvent',
    'BarcodePaymentEvent',
    'DebitPurchaseEvent',
    'DebitPurchaseReversalEvent',
    'BillPaymentEvent',
    'DebitWithdrawalFeeEvent',
    'DebitWithdrawalEvent',
    'PixTransferOutEvent',
    'PixTransferInEvent',
    'PixTransferOutReversalEvent',
    'PixTransferFailedEvent',
    'PixTransferScheduledEvent',
)

DEFAULT_TAG = '#' #TODO não precisar disso, talvez colocar uma ultima coluna com end-line oculto?

class Debt:
    def __init__(self,**kwargs):
        self.payment_charges = []
        self.title = kwargs.get('title')
        self.origin = kwargs.get('origin')
        self.amount = kwargs.get('amount')
        self.category = kwargs.get('category')
        self.timedate = kwargs.get('timedate')
        self.ref_month = kwargs.get('ref_month')
        self.sub_origin = kwargs.get('sub_origin')  if 'sub_origin' in kwargs else ''
        self.details = kwargs.get('details')
        self.debtor = kwargs.get('debtor') if 'debtor' in kwargs else ''
        self.created_date = kwargs.get('created_date') if 'created_date' in kwargs else datetime.now()
        self.external_id = kwargs.get('external_id') if 'external_id' in kwargs else ''
        #TODO: Incluir novos campos
        self.tag = kwargs.get('tag') if 'tag' in kwargs else ''
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
            ID: {}
            """.format(self.title,self.origin,self.amount,self.category,self.timedate,self.ref_month,self.details,self.debtor,self.created_date,self.external_id)

    def __dict__(self):
        return {
        "title": self.title,
        "origin": self.origin,
        "amount": self.amount,
        "category": self.category,
        "timedate": self.timedate,
        "ref_month": self.ref_month,
        "sub_origin": self.sub_origin,
        "debtor": self.debtor,
    }

    def to_list(self):
        return [
            self.title,
            self.origin,
            self.amount,
            self.category,
            self.timedate.strftime("%d/%m/%Y %H:%M:%S"),
            CONST.MONTHS[self.ref_month.month],
            self.sub_origin,
            self.details,
            self.debtor,
            self.created_date.strftime("%d/%m/%Y %H:%M:%S"),
            self.external_id,
            self.tag
        ]
    def __update_values(self):
        origins = DataBase.read_debts_domain('origins')
        if self.origin not in origins:
            origins.append(self.origin)
            DataBase.write_debts_domain('origins',origins)
            #TODO GSheets().append([cat],GS.Categories.table)
            logging.info(f' New ORIGIN domain inserted: {self.origin}')

        categories = DataBase.read_debts_domain('categories')
        if self.category not in categories:
            categories.update({self.category:[]})
            DataBase.write_debts_domain('categories',json.dumps(categories))
            #TODO GSheets().append([cat],GS.Categories.table)
            logging.info(f' New CATEGORY domain inserted: {self.category}')

    def get_payment_charges(self):
        return self.payment_charges

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

    def __get_title(self,text):
        return text
    

    def __get_tag(self):
        dict_ = self.__dict__()
        final_tag = DEFAULT_TAG
        for tag in DataBase.get_tags():
            for field,value in tag.items():
                print(final_tag,field,value)
                if field != 'tag_name' and dict_[field] != value:
                    final_tag = DEFAULT_TAG
                    break
                final_tag = tag['tag_name']
            if final_tag != '':
                return final_tag
        return final_tag

    @staticmethod
    def get_closing_day():
        return int(DataBase.read_debts_domain("closing_day"))

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
                #timedate= datetime.strptime(jsn['time'],"%Y-%m-%dT%H:%M:%SZ"),
                timedate = dateutil.parser.parse(jsn['time']),
                ref_month= self.__get_refmonth(jsn['time']),
                sub_origin = self.__get_suborigin(jsn['details']),
                details= self.__get_details(jsn['details']),
                external_id = self.__get_id(jsn))
        self.tag = self.__get_tag()
        self.__add_payment_charges()

    def __get_refmonth(self,datetime_):
        closing_day = Debt.get_closing_day()
        ref_month = dateutil.parser.parse(datetime_) #,"%Y-%m-%dT%H:%M:%SZ")
        if ref_month.day >= closing_day:
            ref_month = ref_month + relativedelta(months=1)
        return ref_month
    
    def __getamount(self,jsn):
        if 'charges' in jsn['details']:
            self.count = jsn['details']['charges']['count']
            return -int(jsn['details']['charges']['amount'])/100
        return -int(jsn['amount'])/100

    def __get_suborigin(self,jsn):
        if 'subcategory' in jsn:
            if jsn['subcategory'] == 'card_not_present':
                return 'Virtual C.C.'
            elif jsn['subcategory'] == 'card_present':
                return 'Physical C.C.'
        return 'Unknown'

    def __get_details(self,input):
        details = []
        if 'status' in input:
            if input['status'] == 'denied':
               details.append('Purchase Denied') 
        if 'fx' in input:
            details.append('Purchase of {} {} with exchange rate of {} (Equal to {} USD)'.format(input['fx']["currency_origin"], 
                                                                                                 input['fx']["precise_amount_origin"],
                                                                                                 input['fx']["exchange_rate"],
                                                                                                 input['fx']["precise_amount_usd"]))
        return ' | '.join(details)
    
    def __get_id(self,jsn):
        if 'id' in jsn:
            return jsn['id']
        return ''

    def __add_payment_charges(self):
        for c in range(1,self.count):
            copy_input = copy.copy(self)
            copy_input.ref_month = copy_input.ref_month + relativedelta(months=c)
            self.payment_charges.append(copy_input)
    
    def __get_tag(self):
        dict_ = self.__dict__()
        final_tag = DEFAULT_TAG
        for tag in DataBase.get_tags():
            for field,value in tag.items():
                print(final_tag,field,value)
                if field != 'tag_name' and dict_[field] != value:
                    final_tag = DEFAULT_TAG
                    break
                final_tag = tag['tag_name']
            if final_tag != '':
                return final_tag
        return final_tag

class NuAccountDebt(Debt):
    def __init__(self,jsn):
        super().__init__(
                title= jsn['title'],
                origin= "Nuconta",
                amount= self.__getamount(jsn),
                category= self.__get_category(jsn),
                timedate= datetime.strptime(jsn['postDate'],"%Y-%m-%d"),
                ref_month= self.__get_refmonth(jsn['postDate']),
                details=self.__get_details(jsn),
                debtor=self.__get_debtor(jsn['detail']))
        self.tag = self.__get_tag()
        self.__add_payment_charges()

    def __get_category(self,jsn):
        if jsn['footer'] in ['Pix']:
            return 'pix'
        elif jsn['detail'] in ['Nu Reserva Imediata']:
            return 'reserva'
        elif jsn['title'] in ['Pagamento da fatura']:
            return 'pagamento'
        return 'movimentação'
    
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
        if self.title == "Pagamento da fatura" or self.title == "Pagamento de fatura":
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

    def __get_tag(self):
        dict_ = self.__dict__()
        final_tag = DEFAULT_TAG
        for tag in DataBase.get_tags():
            for field,value in tag.items():
                print(final_tag,field,value)
                if field != 'tag_name' and dict_[field] != value:
                    final_tag = DEFAULT_TAG
                    break
                final_tag = tag['tag_name']
            if final_tag != '':
                return final_tag
        return final_tag

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
                sub_origin= jsn[model.sub_origin],
                details= jsn[model.details],
                debtor= jsn[model.debtor],
                created_date= datetime.strptime(jsn[model.created_date],"%d/%m/%Y %H:%M:%S"),
                external_id= jsn[model.external_id],
                tag= jsn[model.tag])

    def __get_refmonth(self,input):
        month_num = 1
        for month in CONST.MONTHS:
            if month == input:
                break
            month_num += 1
        return datetime.now().replace(month=month_num)

class CSVAccountDebt(Debt):
    def __init__(self,description,amount,create_date,id):

        title = self.__get_title(description)
        origin = 'Nuconta'
        amount = amount
        category = self.__get_category(description)
        timedate = datetime.strptime(create_date,"%d/%m/%Y")
        ref_month = self.__get_refmonth(create_date)
        sub_origin = self.__get_suborigin(description)
        details = self.__get_details(description)
        debtor = self.__get_debtor(description)
        created_date = datetime.now()
        external_id = id

        super().__init__(
                title = title,
                origin = origin,
                amount = float(amount),
                category = category,
                timedate = timedate,
                ref_month = ref_month,
                sub_origin = sub_origin,
                details = details,
                debtor = debtor,
                created_date = created_date,
                external_id = external_id)
        
        self.tag = self.__get_tag()
        self.__add_payment_charges()

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
                sub_origin= 'movimentação',
                details= 'Automatic created',
                debtor= '',
            ))
            
    def __get_title(self,text):
        if '-' in text:
            return text.split('-')[0]
        return text

    def __get_category(self,text):
        if 'nu reserva imediata' in text.lower():
            return 'reserva'
        elif 'aplicação' in text.lower():
            return 'aplicação'
        elif 'pagamento da fatura' in text.lower():
            return 'pagamento'
        return 'movimentação'
    
    def __get_suborigin(self,text):
        if 'pix' in text.lower():
            return 'PIX'
        elif 'boleto' in text.lower():
            return 'Boleto'
        elif 'transferência recebida' in text.lower():
            return 'Transferência'
        elif 'compra no débito' in text.lower():
            return 'Débito'
        elif 'aplicação' in text.lower():
            return 'Aplicação'
        return 'movimentação'

    def __get_details(self,text):
        detail = ['CSV Automated']
        details = text.split(' - ')
        details.pop(0) if details else False #Remove Title
        details.pop(0) if details else False #Remove Debtor
        for t in details:
            detail.append(t)
        return " | ".join(detail)
    
    def __get_refmonth(self,datetime_):
        closing_day = Debt.get_closing_day()
        ref_month = datetime.strptime(datetime_,"%d/%m/%Y")
        if ref_month.day >= closing_day:
            ref_month = ref_month + relativedelta(months=1)
        return ref_month
    
    def __get_debtor(self,description):
        split_desc = description.split(' - ') > 1
        if len(split_desc) > 1:
            return split_desc[1]
        #list_ = self.debtor_list()
        #for name in list_:
        #    if name in input:
        #        return name
        #return ''
    
    def __get_tag(self):
        dict_ = dict(self)
        final_tag = DEFAULT_TAG
        for tag in DataBase.get_tags():
            for field,value in tag.items():
                if value == "":
                    break
                if field == 'tag_name':
                    continue
                else:
                    final_tag = tag['tag_name'] if str(dict_[field]) in str(value) else DEFAULT_TAG
            if final_tag != DEFAULT_TAG: #TODO:Append tag
                return final_tag
        return final_tag