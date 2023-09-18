from datetime import timedelta, datetime
from pynubank import Nubank as Nu, MockHttpClient
import os
from dotenv import load_dotenv

#TODO pipenv run pynubank enviar mensagem no telegram, certificado vence depois de alguns meses

class Nubank:

    def __init__(self,prod=True):
        self.cert_file = 'keys/cert.p12'
        self.prod = prod
        if os.getenv('env') == 'PROD' and self.prod:
            self.nu = Nu()                #Ambiente de Produção
        else:
            self.nu = Nu(MockHttpClient()) #Ambiente de TESTE
        self.nu.authenticate_with_cert(os.getenv('nu_log'), os.getenv('nu_pas'), self.cert_file)

    def get_card_statements(self):
        return self.nu.get_card_statements()
    
    def get_account_statements(self):
        return self.nu.get_account_feed_paginated()

    def get_details(self,debt):
        return self.nu.get_card_statement_details(debt)

    def refresh_token(self):
        # O Refresh token pode ser utilizado para fazer logins futuros (Sem senha)
        refresh_token = self.nu.authenticate_with_cert(os.getenv('nu_log'), os.getenv('nu_pas'), self.cert_file)

        # Numa futura utilização é possível fazer o login só com o token
        #self.nu.authenticate_with_refresh_token(refresh_token, 'caminho/do_certificado.p12')