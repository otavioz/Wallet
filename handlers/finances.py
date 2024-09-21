from datetime import  datetime
from finances.debts import Debt
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import logging
from finances.finances import Finances
import consts as CONS


class FinancesHandler:

    async def finances(update,callback=False,file=False):
        if callback:
            text = update.data.split(';')
        elif file:
            text = ['/f','csvnuc',CONS.CSVNUAFILE]
        else:
            text = update.message.text.split(';')

        step = len(text)
        if step == 1:
            keyboard = [
                            [InlineKeyboardButton("Month Expenses", callback_data="/f;expen")],
                            [InlineKeyboardButton("Month Nubank Bill", callback_data="/f;nubill")],
                            [InlineKeyboardButton("Insert lastest transactions", callback_data="/f;insertlastest")],
                            [InlineKeyboardButton("Change Nubank close-bill date", callback_data="/f;closedate")],
                            [InlineKeyboardButton("Edit limit transaction amount", callback_data="/f;limit")],
                            [InlineKeyboardButton("Insert account transactions using CSV", callback_data="/f;csvnuc")],
                            [InlineKeyboardButton("Cancel", callback_data="/cancel")]
                        ]
                
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Please choose:", reply_markup=reply_markup)

        elif step == 2:
            if text[1] == 'expen':
                await update.message.reply_text(FinancesHandler.get_month_expenses(ref_month=Finances().get_current_month()))
            elif text[1] == 'nubill':
                await update.message.reply_text("Help!")
            elif text[1] == 'closedate':
                await update.message.reply_text("Help!")
            elif text[1] == 'insertlastest':
                await update.message.reply_text(FinancesHandler.insert_expenses())
            elif text[1] == 'csvnuc':
                await update.message.reply_text("Just send a csv file containing the statments. Max filesize is 20Mb.")
            elif text[1] == 'limit':
                await update.message.reply_text("Help!")
        elif step == 3:
            if text[1] == 'csvnuc':
                await update.message.reply_text('All records from the last one will be inserted, if the last record inserted is not in the file, they will all be inserted.')
                await update.message.reply_text(FinancesHandler.insert_expenses_from_csv())
        else:
            await update.message.reply_text("Sorry, I didn't understand your request.")

    def insert_expenses_from_csv():
        messages = ''
        try:
            result = Finances().save_csv_account_statements()
        except FileNotFoundError as e:
            result = 0
            messages += '\n No such file.'
            logging.error(' [insert_expenses_from_csv] {}'.format(e))
        except Exception as e:
            result = 0
            messages += '\n Error on inserting files from CSV.'
            logging.error(' [insert_expenses_from_csv] {}'.format(e))
        return '{} records was inserted.{}'.format(result,messages)
    
    def insert_expenses(closing_date=None):
        messages = ''
        try:
            cards = Finances().save_card_statement(closing_date)
        except Exception as e:
            cards = 0
            messages += '\n Error on saving card statements.'
            logging.error(' [insert_expenses - save_card_statement] {}'.format(e))

        try:
            accou = Finances().save_card_statement(closing_date)
        except Exception as e:
            accou = 0
            messages += '\n Error on saving account statements.'
            logging.error(' [insert_expenses - save_account_statements] {}'.format(e))

        return '{} records was inserted.{}'.format(cards+accou,messages)
    
    def get_month_expenses(ref_month):
        origin_list = Debt.origin_list()
        category_list = Debt.category_list()
        limite = Finances.monthly_limit()
        debts = Finances().read_debts(ref_month)
        if len(debts) == 0:
            return 'No debt found.'
        weighty = debts[0]
        for debt in debts:
            origin_list[debt.origin] += debt.amount
            if debt.origin == 'Nubank':
                category_list[debt.category] += debt.amount
                if debt.amount < weighty.amount:
                    weighty = debt
        category_list = sorted(category_list.items(), key=lambda kv: kv[1], reverse=False)

        #TODO a maior numero de compras por categoria, soma do valor e nome da categoria
        amount = round(-origin_list["Nubank"] / limite * 100,2)
        now_day = int(datetime.now().strftime("%d"))
        if now_day <= 16:
            data = str(round((now_day + 14)/30*100,2))
        else:
            data = str(round((now_day - 16)/30*100,2))

        return f'Fatura do Nubank no valor de R${round(-origin_list["Nubank"],2)}, cerca de {amount}% do limite de R${limite} no período de {data}% do mês.'\
            f'\nCompra mais significativa é a <b>{weighty.title}</b> no valor de R${-weighty.amount} feita no dia {weighty.timedate.strftime("%d/%m/%Y")}.'\
            f'\n<b>{category_list[0][0]}</b> foi a categoria com mais gastos, totalizando R${round(-category_list[0][1],2)}.'\
            f'\nTransações na NuConta totalizam R${-round(origin_list["Nuconta"],2)}.'


    def batch():
        logging.info(f' [BATCH] {FinancesHandler.insert_expenses()}')
