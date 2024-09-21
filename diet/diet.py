from google.gsheets import GSheets
from diet.model import HistoryModel
from datetime import datetime
import consts as CONS
from handlers.execeptions import GoogleAPIError

class Diet:

    def insert_meal(self):
        food_list = []
        datenow = datetime.today().strftime('%d/%m/%Y')
        with open(CONS.TRANSFILE, encoding='UTF-8') as file:
            for line in file:
                food_list.append([datenow,line.replace('\n',''),0])
        result = GSheets(sheet='diet_spreadsheet_id').append(food_list, HistoryModel.table)
        #DataBase.write_nubank_domain('last_card_statements', datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%SZ"))
        return result
    