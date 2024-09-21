from google.gsheets import GSheets
from gym.model import EntradaModel,ExerciseModel,HistoryModel
from datetime import datetime

from handlers.execeptions import GoogleAPIError

class Gym:

    def insert_day(self):
        exercise_list = []
        datenow = datetime.today().strftime('%d/%m/%Y')
        resp = GSheets(sheet='gym_spreadsheet_id').get(EntradaModel.table, majorDimension='ROWS')
        if 'values' in resp:
            for d in resp['values']:
                if d[EntradaModel.check]:
                    if '#N/A' in str(d[EntradaModel.id_]): #"#N/A (Did not find value 'Banco Romano' in VLOOKUP evaluation.)"
                        d[EntradaModel.id_] = self.new_exercise(d)
                    exercise_list.append([datenow,
                                          d[EntradaModel.card],
                                          d[EntradaModel.id_],
                                          d[EntradaModel.serie] if len(d) >= 5 else '',
                                          d[EntradaModel.repetition] if len(d) >= 6 else '',
                                          d[EntradaModel.weight] if len(d) >= 7 else '' ])
        result = GSheets(sheet='gym_spreadsheet_id').append(exercise_list, HistoryModel.table)
        #DataBase.write_nubank_domain('last_card_statements', datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%SZ"))
        return result
    
    def new_exercise(self,d):
        new_id = 1
        res = GSheets(sheet='gym_spreadsheet_id').get(ExerciseModel.table, majorDimension='ROWS')
        if 'values' in res:
            new_id = res['values'][-1][ExerciseModel.id] + 1   
        result = GSheets(sheet='gym_spreadsheet_id').append([[d[EntradaModel.name],new_id,'']], ExerciseModel.table)
        if result == 1:
            return new_id
        raise GoogleAPIError('Error while inserting new value on Google Sheets.')