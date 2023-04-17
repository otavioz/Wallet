from datetime import timedelta, datetime
from pynubank import Nubank as Nu, MockHttpClient
import os
from dotenv import load_dotenv

class Nubank:

    def __init__(self,prod=True):
        if os.getenv('env') == 'PROD' and prod:
            self.nu = Nu()                #Ambiente de Produção
            self.prod = True
        else:
            self.nu = Nu(MockHttpClient()) #Ambiente de TESTE
            self.prod = False
        self.nu.authenticate_with_cert(os.getenv('nu_log'), os.getenv('nu_pas'), 'keys/cert.p12')

    def get_card_statements(self):
        return self.nu.get_card_statements()
    
    def get_account_statements(self):
        return self.nu.get_account_statements_paginated()

    def get_details(self,debt):
        return self.nu.get_card_statement_details(debt)
