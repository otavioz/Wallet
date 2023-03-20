﻿from configparser import ConfigParser as CP
import consts as CONS
from ast import literal_eval


class DataBase:

    def read_debts_domain(data):
        config = CP()
        config.read(CONS.DB_FILE_NAME)
        return literal_eval(config.get("DEBTS",data))

    def write_debts_domain(key,value):
        config = CP()
        config.read(CONS.DB_FILE_NAME)
        cnfFile = open(CONS.DB_FILE_NAME, "w",encoding="utf-8")
        config.set("DEBTS",key,value)
        config.write(cnfFile)
        cnfFile.close()
    
    def read_nubank_domain(data):
        config = CP()
        config.read(CONS.DB_FILE_NAME)
        return config.get("NUBANK",data)

    def write_nubank_domain(key,value):
        config = CP()
        config.read(CONS.DB_FILE_NAME)
        cnfFile = open(CONS.DB_FILE_NAME, "w",encoding="utf-8")
        config.set("NUBANK",key,value)
        config.write(cnfFile)
        cnfFile.close()