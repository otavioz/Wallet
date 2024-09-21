from datetime import datetime
import dateutil.parser
import csv
import logging
import os
from datetime import datetime
import logging
import traceback
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
        closing_day = Debt.get_closing_day()
        return today.month if today.day < closing_day else today.month + 1

    def read_debts(self, ref_month=0):
        """
        Read debts from Google Sheets. If ref_month is not passed, all debts will be returned.
        """
        month = CONS.MONTHS[ref_month]
        bills_list = []
        resp = GSheets().get(DebtModel.table, majorDimension='ROWS')
        if 'values' in resp:
            for d in resp['values']:
                if d[DebtModel.ref_month] == month or month == "All":
                    bills_list.append(DriveDebt(d))
        return bills_list

    @staticmethod
    def monthly_limit(origin='Nubank'):
        for l in GSheets().get(MonthlyLimitModel.table, majorDimension='ROWS')['values']:
            if l[MonthlyLimitModel.name] == origin:
                return float(l[MonthlyLimitModel.max_value])
        return 0

    def save_card_statement(self, closing_date=None):
        """
        Get all card statements from Nubank and insert following the last one inserted by the date time.
        """
        base_date = dateutil.parser.parse(DataBase.read_nubank_domain('last_card_statements')) if closing_date is None else dateutil.parser.parse(closing_date)
        bills_list = []
        for transaction in Nubank().get_card_statements():
            date = dateutil.parser.parse(transaction['time'])
            if date > base_date:
                bill = NubankDebt(transaction)
                bills_list.append(bill.to_list())
                bills_list.extend([b.to_list() for b in bill.get_payment_charges()])
        result = GSheets().append(bills_list, DebtModel.table)
        DataBase.write_nubank_domain('last_card_statements', datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%SZ"))
        return result

    def save_account_statements(self):
        """
        Get all account statements from Nubank and insert following the last one inserted by id.
        """
        base_id = DataBase.read_nubank_domain('last_account_id')
        bills_list = []
        transactions = Nubank().get_account_statements()
        last_id = None
        for transaction in transactions['edges']:
            last_id = transaction['node']['id'] if last_id is None else last_id
            if base_id == transaction['node']['id']:
                DataBase.write_nubank_domain('last_account_id', last_id)
                break
            bill = NuAccountDebt(transaction['node'])
            bills_list.append(bill.to_list())
            bills_list.extend([b.to_list() for b in bill.get_payment_charges()])
        if base_id != last_id:
            logging.warning('Last id not found, maybe pagination was required.')
        result = GSheets().append(bills_list, DebtModel.table)
        DataBase.write_nubank_domain('last_account_statements', datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%SZ"))
        return result

    def save_csv_account_statements(self, csv_filename=CONS.CSVNUAFILE):
        """
        Insert statements from CSV file formatted as:

        Data,Valor,Identificador,Descrição
        d/m/Y, -000.00, <str>, <str>

        Since the CSV comes in chronological order, with the oldest first, the code should skip all lines until finding the same ID saved, and only then insert the remaining ones.
        """
        #try:
        base_id = DataBase.read_nubank_domain('last_account_id')
        bills_list = []
        last_id = 0
        with open(csv_filename, encoding='utf-8') as file:
            csv_reader = csv.reader(file, delimiter=',')
            next(csv_reader)  # Skip Header
            for line in csv_reader:
                if base_id == line[2]:
                    break
                last_id = line[2]
                bill = CSVAccountDebt(line[3], line[1], line[0], line[2])
                bills_list.append(bill.to_list())
                bills_list.extend([b.to_list() for b in bill.get_payment_charges()])
            DataBase.write_nubank_domain('last_account_id', last_id)
        os.remove(csv_filename)
        if not bills_list:
            logging.warning('Last id not found, maybe older files are required.')
        result = GSheets().append(bills_list, DebtModel.table)
        DataBase.write_nubank_domain('last_account_statements', datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%SZ"))
        #except FileNotFoundError as e:
        #    result = 0
        #    logging.info(f'[save_csv_account_statements] - {type(e).__name__} {e}')
        #    raise FileNotFoundError(f'No such file {csv_filename}')
        #except Exception as e:
        #    result = 0
        #    logging.error(f'[save_csv_account_statements] - {traceback.format_exc()}') #TODO exception hanlder não capturou o list index out of range
        #    raise e
        #finally:
        #    return result

        



