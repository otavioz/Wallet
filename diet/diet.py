from db.db import DataBase
from google.gsheets import GSheets
from diet.model import HistoryModel
from datetime import datetime
import consts as CONS
from handlers.execeptions import GoogleAPIError

class Diet:

    def insert_meal(self, filename=CONS.TRANSFILE):
        food_list = []
        datenow = datetime.today().strftime('%d/%m/%Y')
        with open(filename, encoding='UTF-8') as file:
            for line in file:
                food,unit = line.replace('\n','').split(',')
                food_list.append([datenow,food,unit])
        result = GSheets(sheet='diet_spreadsheet_id').append(food_list, HistoryModel.table)
        #DataBase.write_nubank_domain('last_card_statements', datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%SZ"))
        return result
    
    
    def get_meals(self, text: str) -> list:
        """
        Identifies the food items and their quantities from the input text, 
        and removes the word 'de' before returning the dish name.

        Args:
            text (str): The input text containing food descriptions.
        
        Returns:
            list: A list of tuples with each tuple containing the food item and its quantity in grams or milliliters.
        """
        # Dictionary to map units to their respective multipliers
        unit_multipliers = {
            ' ml ': 1,
            ' g ': 1,
            ' colheres de sopa ': 15,
            ' colheres de chá ': 5,
            ' colher de sopa ': 15,
            ' colher de chá ': 5,
            ' colheres ': 15,
            ' colher ': 15,
            ' unidades ': 1,
            ' unidade ': 1
        }

        results = []
        text = text.strip().lower()  # Handle spaces and case sensitivity
        for dish in text.split(CONS.DIETCOMMA):
            unit = None
            multiplier = 1
            quantity = 1
            quantity_str = '1'

            # Convert in full numbers to roman numbers
            dish,quantity_str = self.number_converter(dish)

            # Check for unitS and associated multipliers
            for unit_, multiplier_ in unit_multipliers.items():
                if unit_ in dish:
                    unit = unit_
                    multiplier = multiplier_
                    break
            if unit:
                quantity_str = dish.split(unit)[0].strip().replace(' ', '')
                dish = dish.replace(unit, '').strip()

            try:
                dish = dish.replace(quantity_str, '')
                quantity = float(quantity_str)
            except ValueError:
                quantity = 1

            quantity *= multiplier

            # Remove "de" at the beginning of the dish if it exists
            dish = dish.strip()
            if dish.startswith('de '):
                dish = dish[3:]
            results.append((dish, quantity))

        return results
    
    def number_converter(self,text: str) -> str:
        numbers = {'um quarto':1/4,'meia':0.5,'uma':1,'um':1,'dois':2,'três':3,'quatro':4,'cinco':5,'seis':6,'sete':7,'oito':8,'nove':9,'dez':10}
        for num,dec in numbers.items():
            if num in text or str(dec) in text: 
                dec = str(dec)
                text = text.replace(num,dec)
                return text,dec
        return text,'1'
