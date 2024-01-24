from __future__ import print_function
import telebot
import array
import threading
import datetime
from datetime import date
from datetime import datetime
from datetime import timezone
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application
import time
import googleapiclient
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Токен бота, полученный от BotFather
TOKEN = '6852778944:AAFEOIfpSNYgLxmrrEmmbJRMAyhml05w-Fs'

# Список встреч
meets = []

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)

SCOPES = ['https://www.googleapis.com/auth/calendar']

calendarId = 'b37b52c8c527a36b86e376be3f8cdad24093755eda4ebfc1e051648b829a8476@group.calendar.google.com'
SERVICE_ACCOUNT_FILE = 'dotted-furnace-411220-766564afcb27.json'

class GoogleCalendar(object):

    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)

    # вывод списка предстоящих событий
    def get_events_list(self):
        credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)
        meets.clear()
        today = datetime.utcnow()
        timeMin = today.strftime("%Y-%m-%d") + 'T00:00:00.0000Z'
        timeMax = today.strftime("%Y-%m-%d") + 'T23:59:59.0000Z'
        #timeMin = '2024-01-12T00:00:00.0000Z'
        #timeMax = '2024-01-12T23:59:59.0000Z'
        events_result = self.service.events().list(calendarId=calendarId,
                                                   timeMin=timeMin,
                                                   timeMax=timeMax,
                                                   maxResults=50, singleEvents=True,
                                                   orderBy='startTime').execute()
        events = events_result.get('items', [])
        
        if not events:
            #meets.append('Привет!\nНа сегодня собесов нет')
            meets.clear()
            #meets.insert(0, 'Привет!\nВ ближайшие 3 часа собесов нет')
        else:
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                date_obj = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S%z').astimezone(timezone.utc)
                #print(event['start'].get('dateTime'))
                t1 = datetime.strptime(today.strftime("%H:%M:%S"), '%H:%M:%S')
                #t1 = datetime.strptime('16:45:00', '%H:%M:%S')
                t2 = datetime.strptime(date_obj.strftime("%H:%M:%S"), '%H:%M:%S')
                delta = int((t2 - t1).total_seconds() / 60)
                #print(delta)
                if delta in range(31):
                    meets.append(datetime.strptime(start, '%Y-%m-%dT%H:%M:%S%z').strftime("%H:%M") + ' - ' + event['summary'])
            if meets:
                meets.insert(0, '🤖 НАПОМИНАНИЕ:\nЧерез 30 минут')
            else:
                meets.clear()
                #meets.insert(0, 'Привет!\nВ ближайшие 3 часа собесов нет')

calendar = GoogleCalendar()

#@bot.message_handler(commands=['start'])
#def send_today_schedule(message):
#    chat_id = message.chat.id
#    calendar.get_events_list()
#    bot.send_message(chat_id, 'Привет!')
#    bot.send_message(chat_id, '\n'.join(meets))

async def check_meetings(context: ContextTypes.DEFAULT_TYPE):
    calendar.get_events_list() # 294959988  context.job.chat_id
    if meets:
        await context.bot.send_message('-1001875442536', '\n'.join(meets))
        #await context.bot.send_message('-4193321755', '\n'.join(meets))

async def callback_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    name = update.effective_chat.full_name
    context.job_queue.run_repeating(check_meetings, interval=1800, first=10, data=name, chat_id=chat_id)
    #context.job_queue.run_repeating(check_meetings, interval=15, first=5, data=name, chat_id=chat_id)

# главная функция программы
def main():
    application = Application.builder().token(TOKEN).build()
    timer_handler = CommandHandler('start', callback_timer)
    application.add_handler(timer_handler)
    application.run_polling()

    #job_queue = application.job_queue
    #job_minute = job_queue.run_repeating(check_meetings, interval=15, first=5)
    #application.run_polling()

if __name__ == '__main__':
    main()