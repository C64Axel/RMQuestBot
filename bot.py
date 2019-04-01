#! /usr/bin/python

import telepot
import pymysql.cursors
import logging
import sys
import json
import datetime

from telepot.loop import MessageLoop
from time import sleep
from configobj import ConfigObj

# Logging
def log(msg):
	print (msg)
        logging.basicConfig(filename="log/" + botname + ".log", format="%(asctime)s|%(message)s", level=logging.INFO)
        logging.info(msg)

def sendtelegram(chatid,msg):
	try:
		bot.sendMessage(chatid, msg)
        except telepot.exception.TooManyRequestsError:
        	log("To many Requests. Sleep 1 sec.")
        	sleep(1)
	except:
		log ("ERROR IN SENDING TELEGRAM MESSAGE TO {}".format(chatid))

def sendvenue(chatid,latitude,longitude,stopname,pokemonname):
	try:
		bot.sendVenue(chatid,latitude,longitude,stopname,pokemonname)
	except telepot.exception.TooManyRequestsError:
		log("To many Requests. Sleep 1 sec.")
		sleep(1)


# Handle for incomming Commands
def handle(msg):
	content_type, chat_type, chat_id = telepot.glance(msg)
	if content_type != 'text':
		return

	fromwho = msg.get('from')
	username = fromwho.get('username', '')
	vname = fromwho.get('first_name', '')
	nname = fromwho.get('last_name', '')

	log("Message from ID: " + str(chat_id) + ":" + username + ":" + msg['text'])

	commandline = msg['text'].split("@")[0]
	command = commandline.split(" ")[0]
	try:
		parameter = commandline.split(" ",1)[1]
	except:
		parameter = None

	try:
		connection.ping(reconnect=True)
	except:
		sendtelegram(chat_id,msg_loc["2"])
		command=""

	dt = int(datetime.date.today().strftime('%s'))

	if command == "/help":
		msg = ""
		helplist = msg_loc["1"].split("\n")
		for i in helplist:
			msg = msg + "{} :\n{}\n".format(i.split(":")[0].encode("utf-8"),i.split(":")[1].encode("utf-8"))
		bot.sendMessage(chat_id, msg)

	elif command == "/id":
                try:
                        pokemonid = parameter
			pokemonname = pokemon_loc[pokemonid]["name"]
                except:
                        sendtelegram(chat_id,msg_loc["3"])
                        return
                try:
			cursor.execute("select count(*) from trs_quest where quest_timestamp > '%s' and quest_pokemon_id='%s'" % (dt,pokemonid))
	                result = cursor.fetchone()
        	        if result[0] > 0:
                        	cursor.execute("select GUID,quest_task from trs_quest where quest_timestamp > '%s' and quest_pokemon_id='%s'" % (dt,pokemonid))
		                pokestops = cursor.fetchall()
				for row in pokestops:
                        		cursor.execute("select latitude,longitude,name from pokestop where pokestop_id='%s'" % (row[0]))
					pokestop = cursor.fetchone()
					sendvenue(chat_id,pokestop[0],pokestop[1],pokestop[2],pokemonname + "\n" + row[1])

			else:
				sendtelegram(chat_id, msg_loc["4"].format(pokemonname))
                except:
                        sendtelegram(chat_id, msg_loc["2"])

	elif command == "/text":
                try:
                        searchtext = parameter
                except:
                        sendtelegram(chat_id,msg_loc["3"])
                        return
		try:
			cursor.execute("select count(*) from trs_quest where quest_timestamp > '%s' and quest_task like '%s'" % (dt,"%" + searchtext +"%"))
			result = cursor.fetchone()
			if result[0] > 0:
				cursor.execute("select GUID,quest_task from trs_quest where quest_timestamp > '%s' and quest_task like '%s'" % (dt,"%" + searchtext +"%"))
				pokestops = cursor.fetchall()
				for row in pokestops:
					cursor.execute("select latitude,longitude,name from pokestop where pokestop_id='%s'" % (row[0]))
					pokestop = cursor.fetchone()
					sendvenue(chat_id,pokestop[0],pokestop[1],pokestop[2],row[1])
			else:
				sendtelegram(chat_id, msg_loc["4"].format(searchtext))
                except:
                        sendtelegram(chat_id, msg_loc["2"])

        elif command == "/status":
		try:
			cursor.execute("select count(*) from trs_quest where quest_pokemon_id > '0'")
			result = cursor.fetchone()
			if result[0] > 0:
				cursor.execute("select quest_pokemon_id, count(*) from trs_quest where quest_timestamp > '%s' and quest_pokemon_id > '0' group by quest_pokemon_id" % (dt))
				pokemon = cursor.fetchall()
				msg = msg_loc["7"] + "\n"
				msg = msg + msg_loc["8"] + "\n"
				for row in pokemon:
					msg = msg + "{} : {} : {}\n".format(row[0],pokemon_loc[str(row[0])]["name"].encode("utf-8"),row[1])
				while len(msg) > 0:     # cut message to telegram max messagesize
					msgcut = msg[:4096].rsplit("\n",1)[0]
					sendtelegram(chat_id, msgcut)
					msg = msg[len(msgcut)+1:]

			else:
				sendtelegram(chat_id, msg_loc["6"])
                except:
                        sendtelegram(chat_id, msg_loc["2"])
 

def my_excepthook(excType, excValue, traceback, logger=logging):
    logging.error("Logging an uncaught exception",
                 exc_info=(excType, excValue, traceback))

sys.excepthook = my_excepthook


# read inifile
try:
	inifile = "config.ini"
	config = ConfigObj(inifile)
	token=config.get('token')
        db = config['dbname']
        dbhost = config['dbhost']
        dbport = config.get('dbport', '3306')
        dbuser = config['dbuser']
        dbpassword = config['dbpassword']
	locale = config.get('locale', 'de')
except:
	botname = "None"
	log("Inifile not given")
	quit()

# connect to database
#
try:
	connection = pymysql.connect(host=dbhost,
				     user=dbuser,
				     password=dbpassword,
				     db=db,
				     port=int(dbport),
				     charset='utf8mb4',
				     autocommit='True')
	cursor = connection.cursor()
except:
	log("can not connect to database")
	quit()

# get bot information
#
bot = telepot.Bot(token)
try:
	botident = bot.getMe()
	botname = botident['username']
	botcallname = botident['first_name']
	botid = botident['id']
	try:
		cursor.execute("insert into bot values ('%s','%s')" % (botid,botname))
	except:
		pass
except:
        log("Error in Telegram. Can not find Botname and ID")
        quit()


msg_loc = json.load(open("locales/msg_" + locale + ".json"))
pokemon_loc = json.load(open("locales/pokemon_" + locale + ".json"))

# Main Loop
try:

        MessageLoop(bot, handle).run_as_thread()

        log("Bot {} started".format(botname))

        while True:
                sleep(60)

except KeyboardInterrupt:
        pass
