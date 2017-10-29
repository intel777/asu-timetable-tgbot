# asu-timetable-tgbot
Simple time schedule table bot for [ASU](http://mkr.org.ua/) for telegram. 

## Depends on 
* [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
* [xlrd](https://pypi.python.org/pypi/xlrd)
* [xlutils](https://pypi.python.org/pypi/xlutils)
* [beautifulsoup4](https://pypi.python.org/pypi/beautifulsoup4)

All can be easily installed by
`pip3 install python-telegram-bot xlrd xlutils beautifulsoup4`

## Usage
### Commands
* /table <date, optional> - will send you schedule for specified date otherwise for today. Date format DD.MM.YY
* /start - will subscribes you to warnings about schedule changes
* /stop - unsubscribes you


### txtable function
This function will help you get schedule by '/table' command listed below

Firstly, change variable **tg_token** to one that [Botfather](https://t.me/botfather) had gived to you.
Next, you need some information from ASU system that you university using. Open ASU, select your schedule, open developers tools, goto "network" tab, refresh page and see what POST parameters had been sended. Replace **data** dictionary with that info. Then copy URL of schedule page in **url** variable. 

### updateprocessor module
This module will check for scheude updates every hour and if exists, send you .xml document of schedule, also can be used to send schedule(like /table function) by specific time

Mostly, same steps you have done in previous function, but here is some extra variables to edit.
There is couple lines of code:
```python
if(now_time.hour == 5):
  response = txtable('/table')
  bot.sendMessage(chat_id=-1001131185693, text = response, disable_notification = True)
```
This code is responsible for sending schedule by time.
* now_time.hour == 5 - change '5' to hour that you wand to schedule be sended, also you can add `and now_time.minute = N` to be more accurate 
* txtable('/table') - actually a hack. May be fixed in feature.(It actually musn't take any argument to work properly, but I'm not sure)
* chat_id - chat_id in wich it will be sended(replace it by your group's chat id!)
* disable_notification = True - to be quiet

## Licensing
Licensed under WTFPL(Do What The Fuck You Want To Public License)
