from datetime import  datetime
from finances.debts import Debt
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import logging
from nintendo.game import Game
import consts as CONS


class GamesHandler:

    async def games(update,callback=False,file=False):
        if callback:
            text = update.data.split(';')
        elif file:
            #text = ['/g','csvnuc',CONS.CSVNUAFILE]
            await update.message.reply_text("Can't read CSV files here.")
            return
        else:
            text = update.message.text.split(';')

        step = len(text)
        if step == 1:
            keyboard = [
                            [InlineKeyboardButton("Add games on Wishlist", callback_data="/g;addgame")],
                            [InlineKeyboardButton("Edit Wishlist", callback_data="/g;editgame")],
                            [InlineKeyboardButton("Check Wishlisted games", callback_data="/g;checkwish")],
                            [InlineKeyboardButton("Cancel", callback_data="/cancel")]
                        ]
                
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Please choose:", reply_markup=reply_markup)

        elif step == 2:
            if text[1] == 'addgame':
                await update.message.reply_text("WIP!")
            elif text[1] == 'editgame':
                await update.message.reply_text("WIP!")
            elif text[1] == 'checkwish':
                await update.message.reply_text("WIP!")
        else:
            await update.message.reply_text("Sorry, I didn't understand your request.")