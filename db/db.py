import configparser
import json
from configparser import ConfigParser as CP
import json
import consts as CONS
from ast import literal_eval


class DataBase:
    
    @staticmethod
    def _read_domain(domain, data):
        config = configparser.ConfigParser()
        config.read(CONS.DB_FILE_NAME)
        return config.get(domain, data)

    @staticmethod
    def _write_domain(domain, key, value):
        config = configparser.ConfigParser()
        config.read(CONS.DB_FILE_NAME)
        config.set(domain, key, str(value))
        with open(CONS.DB_FILE_NAME, "w", encoding="utf-8") as cnfFile:
            config.write(cnfFile)
    
    @staticmethod
    def read_debts_domain(data):
        return literal_eval(DataBase._read_domain("DEBTS", data))

    @staticmethod
    def write_debts_domain(key, value):
        DataBase._write_domain("DEBTS", key, value)
    
    @staticmethod
    def read_nubank_domain(data):
        return DataBase._read_domain("NUBANK", data)

    @staticmethod
    def write_nubank_domain(key, value):
        DataBase._write_domain("NUBANK", key, value)

    @staticmethod
    def read_currency_domain(data):
        return DataBase._read_domain("CURRENCY", data)

    @staticmethod
    def write_currency_domain(key, value):
        DataBase._write_domain("CURRENCY", key, value)
    
    @staticmethod
    def get_tags():
        with open('db/tagged_purchases.json', encoding='utf-8-sig') as file:
            return json.load(file)
    