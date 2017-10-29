import requests, re, hashlib, time as ttime, datetime, threading, json, logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from xlutils.copy import copy
from xlrd import open_workbook
from bs4 import BeautifulSoup
#logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

print("Parsing config...")
with open('conf.ini', 'r') as configfile:
	config = json.load(configfile)
	configfile.close()

subscribers = config['subs']
last_md5 = ''
tg_token = '<YOUR TELEGRAM TOKEN HERE>'

def txtable(rdate):
	now_time = datetime.datetime.now()
	date = now_time.strftime('%d.%m.%Y')
	time = now_time.strftime('%H:%M:%S')
	rdate = rdate.replace('/table ', '')
	if(rdate == '/table'):
		print(' No date specified. Will use today')
		rdate = date
	else:
		try:
			datetime.datetime.strptime(rdate, '%d.%m.%Y')
		except ValueError:
			return 'Неверный формат даты. Используйте DD.MM.YYYY(31.12.2017)'
	data = {'TimeTableForm[faculty]': 1, 'TimeTableForm[course]': 1, 'TimeTableForm[group]': 951, 'TimeTableForm[date1]': rdate, 'TimeTableForm[date2]': rdate, 'TimeTableForm[r11]': 5, 'timeTable': 0}
	url = 'http://e-rozklad.dut.edu.ua/timeTable/group'
	response = requests.post(url, data=data)
	soup = BeautifulSoup(response.text, 'html.parser')
	table = soup.find_all('table', {'id':'timeTableGroup'})
	lessons = []
	beginings = []
	endings = []
	infos = []
	for table in table:
		for tr in table.find_all('tr'):
			date_correct = False
			for div in tr.find_all('div'):
				if(div.text == rdate):
					date_correct = True
			if(not date_correct):
				continue
			for td in tr.find_all('td'):
				for span in td.find_all('span', {'class': 'lesson'}):
					lessons.append(span.text)
				for span in td.find_all('span', {'class': 'start'}):
					beginings.append(span.text)
				for span in td.find_all('span', {'class': 'finish'}):
					endings.append(span.text)
				for div in td:
					if(div != None):
						try:
							if('data-content' in div.attrs):
								string = div.attrs['data-content'].replace('<br>', '\n')
								string = re.sub(r'\n\s*\n', '\n', string)
								infos.append(string[:string.rfind('\n')])
						except AttributeError:
							pass

	response = ''
	i = 0
	while i < len(lessons):
		response += '[{}][{} - {}]\n{}\n\n'.format(lessons[i], beginings[i], endings[i], infos[i])
		i += 1
	return response

def start(bot, update):
	now_time = datetime.datetime.now()
	date = now_time.strftime('%d.%m.%y')
	time = now_time.strftime('%H:%M:%S')
	print('[{}][{}]New subscribe request by {} from {} chat'.format(date, time, update.effective_user['username'], update.effective_chat['id']))
	if(update.effective_chat['id'] not in subscribers):
		subscribers.append(update.effective_chat['id'])
		print(subscribers)
		config['subs'] = subscribers
		with open('conf.ini', 'w') as configfile:
			json.dump(config, configfile)
			configfile.close()
		print('Subscription added, notifying...')
		update.message.reply_text('Диалог успешно добавлен в список рассылки. Теперь вы будете получать уведомления об изменении расписания, и будете всегда иметь актуальную версию расписания в Exel формате. Для отписки отправьте /stop')
	else:
		print('Subscription alredy exists.')
		update.message.reply_text('Данный диалог уже находится в списке рассылки')

def stop(bot, update):
	now_time = datetime.datetime.now()
	date = now_time.strftime('%d.%m.%y')
	time = now_time.strftime('%H:%M:%S')
	print('[{}][{}]Unsubscribe request by {} from {} chat'.format(date, time, update.effective_user['username'], update.effective_chat['id']))
	if(update.effective_chat['id'] in subscribers):
		subscribers.remove(update.effective_chat['id'])
		print(subscribers)
		config['subs'] = subscribers
		with open('conf.ini', 'w') as configfile:
			json.dump(config, configfile)
			configfile.close()
		print('Subscription removed, notifying...')
		update.message.reply_text('Диалог успешно удален из списка рассылки, вы больше не будете получать уведомления.')
	else:
		print('No subscription found.')
		update.message.reply_text('Диалог не найден в списке подписки')

def table(bot, update):
	now_time = datetime.datetime.now()
	date = now_time.strftime('%d.%m.%Y')
	time = now_time.strftime('%H:%M:%S')
	print('[{}][{}]Time table by date requested.'.format(date, time))
	update.message.reply_text(txtable(update.message.text))

updater = Updater(tg_token)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('stop', stop))
updater.dispatcher.add_handler(CommandHandler('table', table))

def tgbot():
	print('Waiting for messages...')
	updater.start_polling()

def updateprocessor():
	global last_md5
	while True:
		try:
			now_time = datetime.datetime.now()
			date = now_time.strftime('%d.%m.%y')
			time = now_time.strftime('%H:%M:%S')
			bot = updater.bot
			if(now_time.hour == 5):
				response = txtable('/table')
				bot.sendMessage(chat_id=-1001131185693, text = response, disable_notification = True)
			print('[{}][{}]Getting file...'.format(date, time))
			data = {'TimeTableForm[faculty]': 1, 'TimeTableForm[course]': 1, 'TimeTableForm[group]': 951, 'TimeTableForm[date1]': '01.09.2017', 'TimeTableForm[date2]': '31.12.2017', 'TimeTableForm[r11]': 5, 'timeTable': 0}
			url = "http://e-rozklad.dut.edu.ua/timeTable/groupExcel"
			response = requests.post(url, data=data)
			with open('probe.xls', 'wb') as result:
				result.write(response.content)
				result.close()
			rb = open_workbook('probe.xls')
			wb = copy(rb)
			nms = rb.sheet_names()
			idx = rb.sheet_names().index(nms[0])
			wb.get_sheet(idx).name = 'timeTable'
			wb.save('probe.xls')
			print('Comparing tables...')
			md5 = hashlib.md5(open('probe.xls', 'rb').read()).hexdigest()
			print('Old: {}'.format(last_md5))
			print('New: {}'.format(md5))
			if(last_md5 == md5):
				print('No changes found. Sleeping...')
			else:
				print('Changes found. Processing...')
				print('Saving file with original filename...')
				filename = response.headers['content-disposition']
				filename = re.findall("filename=(.+)", filename)[0].replace('"', '')
				with open(filename, 'wb') as result:
					result.write(response.content)
					result.close()
				print('Sending it to subscribers...')
				for chat in subscribers:
					bot.sendDocument(chat_id=chat, document= open(filename, 'rb'), caption= 'Обнаружена новая версия расписания по несовпадению хеш суммы MD5.\nВремя обнаружения: {}'.format(time))
				print('Done. Entering sleep mode...')
			last_md5 = md5
			ttime.sleep(60 * 60)
		except Exception:
			pass

tgbot_task = threading.Thread(target= tgbot).start()
processor_task = threading.Thread(target= updateprocessor).start()