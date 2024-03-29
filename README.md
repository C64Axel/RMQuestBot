# RMQuestBot

Telegram Bot for searching MAD Quests in RM Database

## Installation Guide:

```
pip install -r requirements.txt
```

### Telegram

Create a Telegram Bot.
Copy config.ini.example to config.ini and set the APIToken Variable.

```
token=xxxxxxxxxx      # Bot API Token
locale=de             # Language Settings

dbname=rocketmapdb    # Database name
dbhost=127.0.0.1      # Database hostname
dbport=3306           # Database port
dbuser=rocketmapuser  # Database user
dbpassword=xxxxxxxxx  # Database user password

maxsearchresult=30    # Max results in text search (default 30)
```

## Programs:

1. **rmquestbot.py** is the program for the Telegram bot commands.

   It knows the folowing commands:

   ```
   help - : Help
   id - <PokedexID>: Search for Quests with the PokemonID reward
   kml - <PokedexID>: Download all Quests of the PokemonID as KML-File
   text - <Text>: Search for Quests with <Text> inside
   status - : Show Pokemons get from Quests
   ```
   
   You can use this for the command list in Telegram ;-)

   kml allow the user to download a kml Waypoint file for using 
   with some mapping tools like GPXViewer for Android

## Changes

### 01. Apr 2019

Initial Version

### 29. Sep 2019

Include KML Download

### 2. Feb 2020

Send KML-File when maxsearchresult exceeded
Extend KML with Description

### 5. Nov 2023

Docker Image
