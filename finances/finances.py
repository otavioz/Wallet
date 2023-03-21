from datetime import datetime
from google.gsheets import GSheets
import consts as CONS
from finances.nubank import Nubank
from finances.debts import Debt,DriveDebt,NuAccountDebt,NubankDebt
from finances.model import MonthlyLimitModel,DebtModel
from db.db import DataBase


class Finances:

    def get_current_month(self) -> int:
        today = datetime.now()
        if today.day < Debt.get_closing_day():
            return today.month
        return today.month + 1

    def read_debts(self,ref_month=0):
        """
        Read debts from the Google Sheets, if ref_month is not passed all debts will be returned.
        """
        month = CONS.MONTHS[ref_month]
        bills_list = []
        resp = GSheets().get(DebtModel.table,majorDimension='ROWS')
        if 'values' in GSheets().get(DebtModel.table,majorDimension='ROWS'):
            for d in resp['values']:
                if d[DebtModel.ref_month] ==  month or month == "All":
                    bills_list.append(DriveDebt(d))
        return bills_list

    @staticmethod
    def monthly_limit(origin='Nubank'):
        for l in GSheets().get(MonthlyLimitModel.table,majorDimension='ROWS')['values']:
            if l[MonthlyLimitModel.name] == origin:
                return float(l[MonthlyLimitModel.max_value])
        return 0

    def save_card_statments(self,closing_date=None):
        """
        Get all card statments from Nubank and insert following the last one inserted by the date time.
        """
        base_date = DataBase.read_nubank_domain('last_card_statements') if closing_date == None else closing_date
        base_date = datetime.strptime(base_date,"%Y-%m-%dT%H:%M:%SZ")
        bills_list = []
        for transaction in Nubank().get_card_statements():
            date = datetime.strptime(transaction['time'],"%Y-%m-%dT%H:%M:%SZ")
            if date > base_date:
                bill = NubankDebt(transaction)
                bills_list.append(bill.to_list())
                bills_list.extend([b.to_list() for b in bill.get_payment_charges()])
        DataBase.write_nubank_domain('last_card_statements',datetime.strftime(datetime.now(),"%Y-%m-%dT%H:%M:%SZ"))
        return GSheets().append(bills_list,DebtModel.table)


    def save_account_statements(self,closing_date=None):
        """
        Get all account statments from nubank and insert following the last one inserted by date.
        """
        base_date = DataBase.read_nubank_domain('last_account_statements') if closing_date == None else closing_date
        base_date = datetime.strptime(base_date,"%Y-%m-%dT%H:%M:%SZ")
        bills_list = []
        transactions = Nubank().get_account_statements()
        next_page = transactions['pageInfo']['hasNextPage'] #TODO implementar auto paginação
        for transaction in transactions['edges']:
            transaction = transaction['node']
            date = datetime.strptime(transaction['postDate'],"%Y-%m-%d") #TODO Motivo do duplicado é a falta de HORA no registro, caso seja chamado 2x no dia insere duplicado.
            if date.date() > base_date.date():
                bill = NuAccountDebt(transaction)
                bills_list.append(bill.to_list())
                bills_list.extend([b.to_list() for b in bill.get_payment_charges()])
        DataBase.write_nubank_domain('last_account_statements',datetime.strftime(datetime.now(),"%Y-%m-%dT%H:%M:%SZ"))
        return GSheets().append(bills_list,DebtModel.table)


        



