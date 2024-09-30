from datetime import  datetime
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
import logging
import speech_recognition as sr
from pydub import AudioSegment
import consts as CONS
from diet.diet import Diet


class DietHandler:

    async def diet(update,callback=False,context=None,file=False):

        
        if callback:
            text = update.data #.split(';')
        elif file:
            text = f'/d;audio;{CONS.AUDIOFILE}'
        else:
            text = update.message.text #.split(';')

        if context.user_data['conversation']:
            #text.insert(0,context.user_data['conversation'])
            text = context.user_data['conversation'] + text
        context.user_data['conversation'] = None

        text = text.split(';')
        step = len(text)
        if step == 1:
            keyboard = [
                            [InlineKeyboardButton("Day's Diet", callback_data="/d;day")],
                            [InlineKeyboardButton("Record meal", callback_data="/d;audio")],
                            [InlineKeyboardButton("Cancel", callback_data="/cancel")]
                        ]
                
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Please choose:", reply_markup=reply_markup)

        elif step == 2:
            if text[1] == 'day':
                await update.message.reply_text('WIP!')
            elif text[1] == 'audio':
                context.user_data['conversation'] = '/d;audio;'
                await update.message.reply_text('Please, record and audio telling what are you eating or ate or write it using the follow template:\n[quantity] [grammage] [food],...',entities=ForceReply())
            elif text[1] == 'dishes':
                await update.message.reply_text('Success! Your meal was recorded.')
        elif step == 3:
            if text[1] == 'audio': # and text[2] == CONS.AUDIOFILE:

                if text[2] == CONS.AUDIOFILE:
                    text = DietHandler.audio_transcription()
                else:
                    text = text[2].replace(',',CONS.DIETCOMMA)

                dishes =  'Você acabou de comer o descrito abaixo?\n'
                temp_text = ''
                for n,d in enumerate(Diet().get_meals(text)):
                    dishes += f'{n+1} - {d[0].capitalize()} ({d[1]}g|ml)\n'
                    temp_text += f'{d[0]},{d[1]}\n'
                DietHandler.write_transcription_to_file(temp_text) 

                #dishes += Diet().get_meals(text)
                keyboard = [
                    [InlineKeyboardButton("Yes", callback_data=f'/d;dishes;text')],
                    [InlineKeyboardButton("No", callback_data="/cancel")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                context.user_data['conversation'] = None
                await update.message.reply_text(dishes,reply_markup=reply_markup)
            elif text[1] == 'dishes' and text[2] == 'text':
                await update.message.reply_text(DietHandler.insert_meal())
        else:
            await update.message.reply_text("Sorry, I didn't understand your request.")
    
    def audio_transcription():
        text = ''
        wav_file = DietHandler.__prepare_voice_file(CONS.AUDIOFILE)
        with sr.AudioFile(wav_file) as source:
            audio_data = sr.Recognizer().record(source)
            r = sr.Recognizer()
            text += r.recognize_google(audio_data, language='pt-BR')
        return text
        #dishes = [d for d in text.lower().split(CONS.DIETCOMMA)]
    
    def __prepare_voice_file(path: str) -> str:
        """
        Converts the input audio file to WAV format if necessary and returns the path to the WAV file.
        """
        if os.path.splitext(path)[1] == '.wav':
            return path
        elif os.path.splitext(path)[1] in ('.mp3', '.m4a', '.ogg', '.flac'):
            audio_file = AudioSegment.from_file(
                path, format=os.path.splitext(path)[1][1:])
            wav_file = os.path.splitext(path)[0] + '.wav'
            audio_file.export(wav_file, format='wav')
            return wav_file
        else:
            raise ValueError(
                f'Unsupported audio format: {format(os.path.splitext(path)[1])}')
    
    def write_transcription_to_file(text, output_file=CONS.TRANSFILE) -> None:
        """
        Writes the transcribed text to the output file.
        """
        with open(output_file, 'w', encoding='UTF-8') as f:
            #for d in text.lower().split(CONS.DIETCOMMA):
            f.write(text)
            #    f.write('\n')
    
    def insert_meal():
        messages = ''
        try:
            result = Diet().insert_meal()
        except Exception as e:
            result = 0
            messages += '\n Error on inserting values.'
            logging.error(' [insert_meal] {}'.format(e))
        return '{} records was inserted.{}'.format(result,messages)