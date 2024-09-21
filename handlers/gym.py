from datetime import  datetime
from finances.debts import Debt
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import logging
from gym.gym import Gym
import consts as CONS


class GymHandler:

    async def gym(update,callback=False,file=False):
        if callback:
            text = update.data.split(';')
        else:
            text = update.message.text.split(';')

        step = len(text)
        if step == 1:
            keyboard = [
                            [InlineKeyboardButton("Gym's day", callback_data="/m;day")],
                            [InlineKeyboardButton("Cancel", callback_data="/cancel")]
                        ]
                
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Please choose:", reply_markup=reply_markup)

        elif step == 2:
            if text[1] == 'day':
                await update.message.reply_text(GymHandler.insert_day())
        else:
            await update.message.reply_text("Sorry, I didn't understand your request.")
    
    def insert_day():
        messages = ''
        try:
            result = Gym().insert_day()
        except Exception as e:
            result = 0
            messages += '\n Error on inserting values.'
            logging.error(' [insert_day] {}'.format(e))
        return '{} records was inserted.{}'.format(result,messages)