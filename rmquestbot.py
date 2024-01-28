#! /usr/bin/python

import telepot
import pymysql.cursors
import logging
import sys
import json
import datetime
import simplekml
import io

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
		bot.sendMessage(chatid, msg)
	except:
		log ("ERROR IN SENDING TELEGRAM MESSAGE TO {}".format(chatid))

def sendvenue(chatid,latitude,longitude,stopname,pokemonname):
	try:
		bot.sendVenue(chatid,latitude,longitude,stopname,pokemonname)
	except telepot.exception.TooManyRequestsError:
		log("To many Requests. Sleep 1 sec.")
		sleep(1)

def sendkml(chatid,pokemonname,pokestops):
	kml=simplekml.Kml()
	kml.document.name = pokemonname
	for row in pokestops:
		pnt = kml.newpoint(name=row[2], coords=[(row[1],row[0])])
		pnt.description = row[3]

	f=io.StringIO(kml.kml())
	bot.sendDocument(chatid,(pokemonname + ".kml", f))

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
	command = commandline.split(" ")[0].lower()
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
			msg = msg + u"{} :\n{}\n".format(i.split(":")[0],i.split(":")[1])
		bot.sendMessage(chat_id, msg)

	elif command == "/kml":
		pokemonid = parameter
		try:
			pokemonname = pokemon_loc[pokemonid]["name"]
		except:
			pokemonname = "?????"
		try:
			cursor.execute("select count(*) \
					from trs_quest \
					where quest_timestamp > '%s' \
						and quest_pokemon_id='%s'" % (dt,pokemonid))
			result = cursor.fetchone()
			if result[0] > 0:
				cursor.execute("select latitude,longitude,name,quest_task \
						from pokestop \
						inner join trs_quest on (GUID = pokestop_id) \
						where quest_timestamp > '%s' \
							and quest_pokemon_id='%s'" % (dt,pokemonid))
				pokestops = cursor.fetchall()
				sendkml(chat_id,pokemonname,pokestops)

			else:
				sendtelegram(chat_id, msg_loc["4"].format(pokemonname))
		except:
			sendtelegram(chat_id, msg_loc["2"])
			raise

	elif command == "/id":
		pokemonid = parameter
		try:
			pokemonname = pokemon_loc[pokemonid]["name"]
		except:
			pokemonname = "?????"
		try:
			cursor.execute("select count(*) \
					from trs_quest \
					where quest_timestamp > '%s' \
						and quest_pokemon_id='%s'" % (dt,pokemonid))
			result = cursor.fetchone()
			if result[0] > 0:
				cursor.execute("select latitude,longitude,name,quest_task \
						from trs_quest \
						inner join pokestop on (GUID = pokestop_id) \
						where quest_timestamp > '%s' \
							and quest_pokemon_id='%s'" % (dt,pokemonid))
				pokestops = cursor.fetchall()
				for row in pokestops:
					sendvenue(chat_id,row[0],row[1],row[2],pokemonname + "\n" + row[3])

			else:
				sendtelegram(chat_id, msg_loc["4"].format(pokemonname))
		except:
			sendtelegram(chat_id, msg_loc["2"])
			raise

	elif command == "/text":
		searchtext = parameter
		if not searchtext:
			sendtelegram(chat_id,msg_loc["9"])
			return

		try:
			cursor.execute("select count(*) \
					from trs_quest \
					where quest_timestamp > '%s' \
						and quest_task like '%s'" % (dt,"%" + searchtext +"%"))
			result = cursor.fetchone()
			if result[0] > 0:
				cursor.execute("select latitude,longitude,name,quest_task \
						from trs_quest \
						inner join pokestop on (GUID = pokestop_id) \
						where quest_timestamp > '%s' \
							and quest_task like '%s'" % (dt,"%" + searchtext +"%"))
				pokestops = cursor.fetchall()
				if result[0] < maxsearch:
					for row in pokestops:
						sendvenue(chat_id,row[0],row[1],row[2],row[3])
				else:
					sendtelegram(chat_id, msg_loc["10"].format(maxsearch))
					sendkml(chat_id,"text",pokestops)
					
			else:
				sendtelegram(chat_id, msg_loc["4"].format(searchtext))
		except:
			sendtelegram(chat_id, msg_loc["2"])
			raise

	elif command == "/status":
		try:
			cursor.execute("select count(*) \
					from trs_quest \
					where quest_pokemon_id > '0'")
			result = cursor.fetchone()
			if result[0] > 0:
				cursor.execute("select quest_pokemon_id, count(*) \
						from trs_quest \
						where quest_timestamp > '%s' \
							and quest_pokemon_id > '0' \
						group by quest_pokemon_id" % (dt))
				pokemon = cursor.fetchall()
				msg = msg_loc["7"] + "\n"
				msg = msg + msg_loc["8"] + "\n"
				for row in pokemon:
					try:
						pokemonname = pokemon_loc[str(row[0])]["name"]
					except:
						pokemonname = "?????"
					msg = msg + u"{} : {} : {}\n".format(row[0],pokemonname,row[1])
				while len(msg) > 0:     # cut message to telegram max messagesize
					msgcut = msg[:4096].rsplit("\n",1)[0]
					sendtelegram(chat_id, msgcut)
					msg = msg[len(msgcut)+1:]

			else:
				sendtelegram(chat_id, msg_loc["6"])
		except:
			sendtelegram(chat_id, msg_loc["2"])
			raise


def my_excepthook(excType, excValue, traceback, logger=logging):
	logging.error("Logging an uncaught exception",
		exc_info=(excType, excValue, traceback))

sys.excepthook = my_excepthook


# read inifile
try:
	inifile = "config.ini"
	config = ConfigObj(inifile)
	token = config.get('token')
	db = config['dbname']
	dbhost = config['dbhost']
	dbport = int(config.get('dbport', '3306'))
	dbuser = config['dbuser']
	dbpassword = config['dbpassword']
	locale = config.get('locale', 'de')
	maxsearch = int(config.get('maxsearchresult', '30'))
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
		port=dbport,
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
except:
	log("Error in Telegram. Can not find Botname and ID")
	quit()


msg_loc = json.load(open("locales/msg_" + locale + ".json"))
pokemon_loc = json.load(open("locales/monster_" + locale + ".json"))

# Main Loop
try:

	MessageLoop(bot, handle).run_as_thread()

	log("Bot {} started".format(botname))

	while True:
		sleep(60)

except KeyboardInterrupt:
	pass
