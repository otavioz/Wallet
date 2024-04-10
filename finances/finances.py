from datetime import datetime
import logging
from google.gsheets import GSheets
import consts as CONS
from finances.nubank import Nubank
from finances.debts import Debt,DriveDebt,NuAccountDebt,NubankDebt,CSVAccountDebt
from finances.model import MonthlyLimitModel,DebtModel
from db.db import DataBase
import csv
import os
import dateutil.parser

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

    def save_card_statement(self,closing_date=None):
        """
        Get all card statments from Nubank and insert following the last one inserted by the date time.
        """
        base_date = DataBase.read_nubank_domain('last_card_statements') if closing_date == None else closing_date
        base_date = dateutil.parser.parse(base_date)
        bills_list = []
        for transaction in Nubank().get_card_statements():
            #date = datetime.strptime(transaction['time'],"%Y-%m-%dT%H:%M:%SZ")
            date = dateutil.parser.parse(transaction['time'])
            if date > base_date:
                bill = NubankDebt(transaction)
                bills_list.append(bill.to_list())
                bills_list.extend([b.to_list() for b in bill.get_payment_charges()])
        result = GSheets().append(bills_list,DebtModel.table)
        DataBase.write_nubank_domain('last_card_statements',datetime.strftime(datetime.now(),"%Y-%m-%dT%H:%M:%SZ"))
        return result
        
    def save_account_statements(self):
        """
        Get all account statments from nubank and insert following the last one inserted by id.
        """

        base_id = DataBase.read_nubank_domain('last_account_id')
        bills_list = []
        transactions = Nubank().get_account_statements()
        next_page = transactions['pageInfo']['hasNextPage'] #TODO implementar auto paginação
        last_id = None
        for transaction in transactions['edges']:
            last_id = transaction['node']['id'] if last_id is None else last_id
            if base_id == transaction['node']['id']:
                DataBase.write_nubank_domain('last_account_id',last_id)
                base_id = last_id
                break
            bill = NuAccountDebt(transaction['node'])
            bills_list.append(bill.to_list())
            bills_list.extend([b.to_list() for b in bill.get_payment_charges()])
        if base_id != last_id:
            logging.warning(f'Last id not found, maybe pagination was required.')
        result = GSheets().append(bills_list,DebtModel.table)
        DataBase.write_nubank_domain('last_account_statements',datetime.strftime(datetime.now(),"%Y-%m-%dT%H:%M:%SZ"))
        return result

    def save_csv_account_statements(self,csv_filename=CONS.CSVNUAFILE):
        """
        Insert statements from CSV file formarted as:

        Data,Valor,Identificador,Descrição
        d/m/Y, -000.00, <str>, <str>

        Como o CSV vem em ordem cronológica, as mais antigas primeiro, o código deve pular todas as linhas até encontrar o mesmo ID
        salvo, só ai inserir as restantes.
        """
        try:
            base_id = DataBase.read_nubank_domain('last_account_id')
            bills_list = []
            last_id = 0
            file = open(csv_filename,encoding='utf-8') #TODO: FileNotFoundError: [Errno 2] No such file or directory: 'NU_35863474_01AGO2023_31AGO2023.csv'
            csv_reader = csv.reader(file, delimiter=',')
            next(csv_reader) #Pular Header          
            for line in csv_reader:
                #if base_id == line[2]:
                #    next_ = True
                #    continue
                if base_id == line[2]:
                    bills_list = [] #Registros já inseridos. Não incluir
                    continue
                last_id = line[2]
                bill = CSVAccountDebt(line[3],line[1],line[0],line[2])
                bills_list.append(bill.to_list())
                bills_list.extend([b.to_list() for b in bill.get_payment_charges()])
            DataBase.write_nubank_domain('last_account_id',last_id)
            file.close()
            os.remove(csv_filename)
            if len(bills_list) < 1:
                logging.warning(f'Last id not found, maybe older files are required.')
            result = GSheets().append(bills_list,DebtModel.table)
            DataBase.write_nubank_domain('last_account_statements',datetime.strftime(datetime.now(),"%Y-%m-%dT%H:%M:%SZ"))
        except FileNotFoundError:
            result = 0
            raise FileNotFoundError(f'No such file {csv_filename}') 
        except Exception as e:
            result = 0
            logging.error(f'[save_csv_account_statements] - {e}') #TODO exception hanlder não capturou o list index out of range
            raise e
        finally:
            return result

        



