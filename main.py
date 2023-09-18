import logging
from telegram import ForceReply, Update
import pytz
import datetime as dtm
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, Defaults,filters
import os
from dotenv import load_dotenv
import time as ttime
from datetime import timedelta, datetime
import traceback
from googleapiclient import errors
from threading import Thread
from handlers.finances import FinancesHandler
from pynubank import exception as NuException
import consts as CONS


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO,filename=f'log.log'
)
logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

async def finances(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Data about the finances"""
    await FinancesHandler.finances(update=update)

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    #TODO não funciona com botões na mesma linha
    selected = [i[0].text for i in query.message.reply_markup.inline_keyboard if i[0].callback_data == query.data][0]
    await query.edit_message_text(text=f'✅ {selected}')
    
    if '/cancel' in query.data:
        await update.message.reply_text('✌')
    elif '/finances' in query.data:
        await FinancesHandler.finances(update=query,callback=True)
    else:
        await update.message.reply_text('Not implemented function.')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def downloader(update, context):
    if update.message.document.mime_type != 'text/csv':
       await update.message.reply_text('The file must be an CSV.')
    else:
        file = await context.bot.get_file(update.message.document)
        await file.download_to_drive(CONS.CSVNUAFILE)
        await FinancesHandler.finances(update=update,file=True)
        #await update.message.reply_text('File donwloaded')
    
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    #await update.message.reply_text(update.message.text)
    await update.message.reply_text('Use /help to know what I can do!')

def batch():
    start_hour = 5
    logging.info(f' Batch is running.')
    while True:
        try:
            now = datetime.now()
            ttime.sleep(59)
            if now.hour == start_hour and now.minute == 50:  #Atualizar Planilha
                logging.info(f' Batch processing started.')
                FinancesHandler.batch()
                logging.info(f' Batch processing ended with success.')
                ttime.sleep(36000) #Sleeping for 10h
        except errors.HttpError as e:
            logging.error(f' Error while calling Google Sheets API {e}')
        except UnicodeDecodeError as e:
            logging.error(f' Unicode error while reading csv file: {e}')
        except NuException.NuRequestException as e:
            logging.error(f' Failed while calling PyNubank: {e}')
        except Exception as e:
            logging.error(f' Batch process failed: {traceback.format_exc()}')
    #TODO: Métodos de catch de erros, criar próprias exceptions nas extremidaddes?

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    defaults = Defaults(parse_mode=ParseMode.HTML, tzinfo=pytz.timezone('America/Sao_Paulo'))
    application = Application.builder().get_updates_http_version('1.1').http_version('1.1').token(os.getenv('bot_token')).defaults(defaults).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("finances", finances))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(callback))

    #File handler
    application.add_handler(MessageHandler(filters.Document.ALL, downloader))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))


    #Batch thread
    if os.getenv('env') == 'PROD':
        t = Thread(target=batch, daemon=True)
        t.start()
        print('[BATCH is running]')

    # Run the bot until the user presses Ctrl-C
    print('[application polling running]')
    application.run_polling()

if __name__ == "__main__":
    main()