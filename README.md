# RMTGBot

Telegram Bot for searching MAD Quests in RM Database

## Installation Guide:

```
pip install -r requirements.txt
```

### Telegram

Create a Telegram Bot and put the APIToken in the Bot.ini File.

```
token=xxxxxxxxxx      # Bot API Token
locale=de             # Language Settings

dbname=tgbotdb        # Database name
dbhost=127.0.0.1      # Database hostname
dbport=3306           # Database port
dbuser=rocketmapuser  # Database user
dbpassword=xxxxxxxxx  # Database user password
```

## Programs:

** All programs need the inifile as their first parameter. **

1. **bot.py** is the program for the Telegram bot commands.

   It knows the folowing commands:

   ```
   help - : Help
   id - <PokedexID>: Search for Quests with the PokemonID reward
   text - <Text>: Search for Quests with <Text> inside
   ```
   
   You can use this for the command list in Telegram ;-)

## Changes

### XX. XXX 2010

Initial Version

