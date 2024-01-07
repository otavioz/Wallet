"""
List os classes based on Google Sheet structured data.
"""

import os
from dotenv import load_dotenv

base = 'Geral'
debt = '2024' if os.getenv('env') == 'PROD' else 'Teste'

class ArrearModel:
    table = f'{base}!B5:F35'
    name = 0
    value = 1
    reason = 2
    status = 3
    last_att = 4

class MonthlyLimitModel:
    table = f'{base}!H4:K10'
    name = 0
    max_value = 1
    value = 2
    origin = 3

class CategoryModel:
    table = f'{base}!M4:P35'
    name = 0 
    is_active = 1
    value_1 = 2
    value_2 = 3

class DebtModel:
    table = f'{debt}!A14:K900'
    title= 0
    origin= 1
    amount= 2
    category= 3
    timedate= 4
    ref_month= 5
    details= 6
    debtor= 7
    created_date= 8
    external_id = 9
    tags = 10