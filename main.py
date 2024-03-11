import html
import json
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
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.WARNING,filename=f'log.log'
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
    elif '/f' in query.data:
        await FinancesHandler.finances(update=query,callback=True)
    else:
        await update.message.reply_text('Not implemented function.')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def downloader(update, context):
    if update.message.document.mime_type != 'text/csv' and update.message.document.mime_type != 'text/comma-separated-values':
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

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logging.error("Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    #tb_string = "".join(tb_list)
    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    #update_str = update.to_dict() if isinstance(update, Update) else str(update)
    #message = (
    #    "An exception was raised while handling an update\n"
    #    f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
    #    "</pre>\n\n"
    #    f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
    #    f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
    #    f"<pre>{html.escape(tb_string)}</pre>"
    #)
    message = (f"Warning: \n{html.escape(tb_list[-1]).split(':')[-1]}")
    # Finally, send the message
    await context.bot.send_message(chat_id=os.getenv('mychat_id'), text=message, parse_mode=ParseMode.HTML
    )

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

    #Error handler
    application.add_error_handler(error_handler)

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