import gspread as gs
import pandas as pd
#from dotenv import load_dotenv
import discord
import os
intents = discord.Intents.all()
intents.members = True

#################################### login to google sheets and return a dataframe from it #############################
gc = gs.service_account('C:/Users/Shoerack/Desktop/credentials.json') #opening credentials json for loging in to google sheets (Change the path for your credentials.json export from google sheets)

sh = gc.open_by_url(INSERT_YOUR_SHEETS_LINK) #opening the google sheets from link

ws = sh.worksheet('dkpbot') #choosing the spreadsheet to work with

pd.options.mode.chained_assignment = None
###################################################variable land########################################################

boss = None
expected_headers = ws.row_values(1)


#---------------------------------Discord bot code aka dkpbot-----------------------------------------------------------
#load_dotenv()
TOKEN = ('INSERT_YOUR_TOKEN_HERE') #discord bot authorization
client = discord.Client(command_prefix=".", intents=intents) #*intents for discord updates on bots.


@client.event #loging in the bot
async def on_ready():
	print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
	username = str(message.author).split('#')[0]
	user_message = str(message.content)
	channel = str(message.channel.name)
	print(f'{username}: {user_message} ({channel})') # reading out messages from discord to python console in format contained in this command.
	chnl = client.get_channel(1005950521082908833) #creating a variable to enable message sending to another channel


	if message.author == client.user:
		return

	if message.channel.name == 'dkpbot':
		if message.content.lower().startswith('!'):  #bot command message needs to start with an exclamation mark (!)
			df = pd.DataFrame(ws.get_all_records(expected_headers = expected_headers))  # reading through the sheet and placing info into the dataframe of pandas.
			df.set_index('DISCORDID',inplace=True)  # setting up the index of the dataframe to be the Discord id of clan member.
			boss = message.content.split()    # boss[0] will represent boss name(row) , boss[1] will represent count(has to contain a value!) , boss[2] and further will represent discord id(columns)

			if not boss[1].startswith('<'):       #fail safe in case no number is writen to use '1' as a counter.
				for i in range(2, len(boss)):     #go through the list of discord ids starting at possition 2 of boss list mentioned above.
					df[boss[0]][boss[i]] = df[boss[0]][boss[i]] + int(boss[1])
					await message.channel.send(boss[i]+'  '+boss[0]+' has been changed by: '+ boss[1]) #send out a response confirming the action into same channel
			else:
				for i in range(1, len(boss)):
					df[boss[0]][boss[i]] = df[boss[0]][boss[i]] + 1
					await message.channel.send(boss[i] + '  ' + boss[0] + ' has been changed by: ' + '1')

			ws.update('B2', df.values.tolist()) #updating google sheets with new values(actually overwriting the whole sheet.) - could be improved with different design to update cell by cell but in my oppinion this is quicker done on local machine or host and throwing whole page at google sheets.

			await chnl.send(str(message.author)+' -       ' + message.content) #sending a message to seperate channel 'dkplog' containing author of command and message content for future debuging and loging.


		else:
			await message.channel.send('You have messed something up!!!')


client.run(TOKEN)