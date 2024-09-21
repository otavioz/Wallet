from datetime import  datetime
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import logging
import speech_recognition as sr
from pydub import AudioSegment
import consts as CONS
from diet.diet import Diet


class DietHandler:

    async def diet(update,callback=False,file=False):
        if callback:
            text = update.data.split(';')
        elif file:
            text = ['/d','audio',CONS.AUDIOFILE]
        else:
            text = update.message.text.split(';')

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
                await update.message.reply_text('Please, record and audio telling what are you eating or ate.')
            elif text[1] == 'dishes':
                await update.message.reply_text('Success! Your meal was recorded.')
        elif step == 3:
            if text[1] == 'audio' and text[2] == CONS.AUDIOFILE:
                text = DietHandler.audio_transcription()
                DietHandler.write_transcription_to_file(text)

                dishes =  'Você acabou de comer o descrito abaixo?\n'
                for n,d in enumerate(text.lower().split(CONS.DIETCOMMA)):
                    dishes += f'{n+1} - {d.title()}\n'
    
                keyboard = [
                    [InlineKeyboardButton("Yes", callback_data=f'/d;dishes;text')],
                    [InlineKeyboardButton("No", callback_data="/cancel")]]
                reply_markup = InlineKeyboardMarkup(keyboard)

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
            for d in text.lower().split(CONS.DIETCOMMA):
                f.write(d)
                f.write('\n')
    
    def insert_meal():
        messages = ''
        try:
            result = Diet().insert_meal()
        except Exception as e:
            result = 0
            messages += '\n Error on inserting values.'
            logging.error(' [insert_meal] {}'.format(e))
        return '{} records was inserted.{}'.format(result,messages)