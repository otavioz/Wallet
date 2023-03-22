import re
from datetime import timedelta, datetime
import os
from pathlib import Path
import time as ttime
from finances.debts import Debt
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import logging
import traceback
from finances.finances import Finances


class FinancesHandler:

    async def finances(update,text=None):
        try:
            text = update.message.text.split(';') if text == None else text.split(';')
            step = len(text)
            if step == 1:
                keyboard = [
                                [InlineKeyboardButton("Month Expenses", callback_data="/finances;expen")],
                                [InlineKeyboardButton("Month Nubank Bill", callback_data="/finances;nubill")],
                                [InlineKeyboardButton("Change Nubank close-bill date", callback_data="/finances;closedate")],
                                [InlineKeyboardButton("Insert lastest transactions", callback_data="/finances;insertlastest")],
                                [InlineKeyboardButton("Edit limit transaction amount", callback_data="/finances;limit")],
                                [InlineKeyboardButton("Cancel", callback_data="/cancel")]
                            ]
                    
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text("Please choose:", reply_markup=reply_markup)

            elif step == 2:
                if text[1] == 'expen':
                    await update.message.reply_text(
                        FinancesHandler
                        .get_month_expenses(ref_month=Finances().get_current_month()))
                elif text[1] == 'nubill':
                    await update.message.reply_text("Help!")
                elif text[1] == 'closedate':
                    await update.message.reply_text("Help!")
                elif text[1] == 'insertlastest':
                   await update.message.reply_text(FinancesHandler.insert_expenses())
                elif text[1] == 'limit':
                    await update.message.reply_text("Help!")
            #elif step == 3:
            #    pass
            else:
                raise ValueError("Error processing your request.")
        except Exception as e :
            logging.error(f'{datetime.now()} - Error processing the request: {e}  Traceback: {traceback.format_exc()}')
            await update.message.reply_text("Something wrong happened!!")

    def insert_expenses(closing_date=None):
        qtd = Finances().save_card_statments(closing_date)
        qtd += Finances().save_account_statements(closing_date)
        return f'{qtd} records was inserted.'
    
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
        logging.info(f'{datetime.now()} - [BATCH] {FinancesHandler.insert_expenses()}')
