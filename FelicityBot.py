#Code written by Tradam --> https://github.com/realtradam

import os

import discord
import random
import json
import re #regular expression
from mcstatus import MinecraftServer #Use 'python3 -m pip install mcstatus' to install, required for minecraft capabilities
from dotenv import load_dotenv #Substitues the API key variable


#This is the generic conversion that works on any server.
#Uses generic messages
				
storedEmojiUniversal = {"!cheer": "<a:cheated:690837457440210945>", 
				"!stress": "<a:stressed:690851643863990302>",
				"!dance": "<a:dance:690853091704176660>",
				"🦜": "<a:partyparrot:691049985264975933>",
				"!trash": "<a:blobtrash:691090868123467866>",
				"!jojo": "<a:jotarodance:691090868513538048>",
				"!bongo": "<a:bongoowo:691090866965839912>"}

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')# You need to set up a .env file which holds your token
EMOJI_SET = os.getenv('EMOJI_SET')#get your custom made emoji set specifically for a server
IP = os.getenv('IP')#IP of your minecraft server
PORT = int(os.getenv('PORT'))#Port of your minecraft server
UNIQUE_SERVER = os.getenv('UNIQUE_SERVER')#ID of your unique server, that can handle special emoji's
MC_FOLDER = os.getenv('MC_FOLDER')#Folder of where you minecraft server/script resides
MC_RUNNABLE_SCRIPT = os.getenv('MC_RUNNABLE_SCRIPT')#Name of your script/server file
PID_TXT = os.getenv('PID_TXT')#Where the PID of your server is stored(to shut it down when you want to)

client = discord.Client()

#Sets up the bot, its variables, etc. when the bot is initially run
@client.event
async def on_ready():
	global storedStats, storedEmojiUnique
	print('{}(id: {}) is connected to the following servers:'.format(client.user,client.user.id))
	for guild in client.guilds:
		print('\t- {} (id: {})'.format(guild.name,guild.id))
	await client.change_presence(status = 'None', activity=discord.Game('you like a damn fiddle'))
	
	#Loads up the statistics of players using the !attack command
	jsonFile = open('attacks.json')
	jsonStr = jsonFile.read()
	storedStats = json.loads(jsonStr)
	#Format of the json data:
	#	{userid : {hp : num, damage : num, death: num}, etc.}
	
	#This sets up another emoji set that can be used on a specific server that
	#	has specific replacable emojis set up
	jsonFile = open(EMOJI_SET)
	jsonStr = jsonFile.read()
	storedEmojiUnique = json.loads(jsonStr)
	
	print("save data loaded")
	print('Bot is live!')
#            break

#Invoked whenever a message is sent in a server
@client.event
async def on_message(message):
	#Variable set up
	global storedStats, storedEmojiUnique, storedEmojiUniversal
	#Used for user identification
	isVerified = "false"
	isAdmin = "false"
	#Address to server
	mcServer = MinecraftServer(IP, PORT)
	
	#If the bot sent the message, ignore
	if message.author == client.user:
		return
		
	#Determines user permissions(will later check agaisnt role name)
	for item in message.author.roles:
		if(str(item) == "Minecraft"):
			isVerified = "true"
		if(str(item) == "ADMIN"):
			isAdmin = "true"
	
	#Depending on which server the message was in: what emoji set should be used
	if str(message.guild.id) == str(UNIQUE_SERVER):
		animatedEmoji = storedEmojiUnique
	else: #All other servers use the generic set
		animatedEmoji = storedEmojiUniversal
	
	#Show info about the minecraft server
	if message.content.lower() == "!mc":
		if(isVerified == "true"):
			try:
				status = mcServer.status()
				query = mcServer.query()
				players = query.players.online
				if players == 0:
					await message.channel.send("The server is Online with no active players")
				elif players == 1:
					await message.channel.send("The server is Online with 1 active player: {}".format(", ".join(query.players.names)))
				elif players > 1:
					await message.channel.send("The server is Online with {} active players: {}".format(players, ", ".join(query.players.names)))
			except ConnectionError:
				await message.channel.send("Server is Offline (Unless it has just been booted up)")
		else:
			await message.channel.send("You do not have permission to do that")
			
	#Run the mc server, if it is not running
	if message.content.lower() == "!mcstart":
		if(isVerified == "true"):
			try:
				status = mcServer.status()
				await message.channel.send("The server is already Online!")
			except ConnectionError:
				os.system('(cd {}; ./{})'.format(MC_FOLDER, MC_RUNNABLE_SCRIPT))#Run a script that will correctly start your server
				await message.channel.send("Server is Offline. Bootup has started, it usually takes up to about 2 minutes to finish booting and become visible online so please be patient")
				return
			return
		else:
			await message.channel.send("You do not have permission to do that")
	
	#Stop the mc server, if it is empty
	if message.content.lower() == "!mcstop":
		if(isVerified == "true"):
			try:
				status = mcServer.status()
				players = status.players.online
				if players > 0:
					await message.channel.send("The server still has players on it! The server must be empty before shutdown can happen")
				else:
					with open ("{}".format(PID_TXT), "r") as myfile: #path to text file that stores the PID of the minecraft server, so that the server can be told to shut down
						pid = myfile.read()
					os.system("kill -15 {}".format(pid))
					await message.channel.send("Server has shut down")
			except ConnectionError:
				await message.channel.send("The server is already Offline (Or if you just booted it up, hasn't come Online yet)")
		else:
			await message.channel.send("You do not have permission to do that")
	
	#Splits the message, so the first word can be matched to a command, and use the rest of the words as parameters
	splitMessage = message.content.lower().split()
	if (len(splitMessage) == 2): #If the command has a parameter
		if (splitMessage[0] == "!react"):
			for emoji in animatedEmoji:
				if splitMessage[1] == emoji:
					await message.delete()
					async for react in message.channel.history(limit=1):
						await react.add_reaction(animatedEmoji[emoji])
						return
			return
		
		if (splitMessage[0] == "!delete"):
			if (isAdmin == "true"):
				#This can be optimized by sending a batch delete rather then increment once
				#It's somehwere in the discord.py api
				async for delete in message.channel.history(limit=(int(splitMessage[1])+1)):
					await delete.delete()
				return
			else:
				message.channel.send('You do not have permission to do that')
				return
		
		if (splitMessage[0] == '!attack'):
			#A little game where users can attack eachother
			#These variable names NEED to be cleaned up
			messageParameter = splitMessage[1]
			targetUserID = [messageParameter[:2],messageParameter[2:-1],messageParameter[-1:]]#This isolates just the ID number of the targeted user
			if targetUserID[1][:1] == '!':#Sometimes discord leaves an ! in the id, but sometimes not. Not sure why but this purges it as it causes bugs with storing data(duplicated users)
				targetUserID[1] = targetUserID[1][1:]
			if targetUserID[0] == '<@' and targetUserID[2] == '>':#After formatting the code, if it is correctly formatted
				if int(targetUserID[1]) == int(client.user.id):#Checks if it was the bot that was targeted in the attack
					await message.channel.send('<a:angryAwooGlitch:691087516819914772>')
					return
				damage = random.randint(1,29)
				if str(message.author.id) not in storedStats:
					storedStats[str(message.author.id)] = {'hp' : 50, 'damage' : 0, 'deaths' : 0}
				elif str(targetUserID[1]) not in storedStats:
					storedStats[str(targetUserID[1])] = {'hp' : 50, 'damage' : 0, 'deaths' : 0}
				
				storedStats[str(targetUserID[1])]['hp'] -= damage
				if storedStats[str(targetUserID[1])]['hp'] <= 0:
					storedStats[str(targetUserID[1])]['deaths'] += 1
					storedStats[str(targetUserID[1])]['hp'] = 50
					if str(message.author.id) == str(targetUserID[1]):
						await message.channel.send('<a:blobhang:691023822576549930>')
						await message.channel.send('<@{}> killed themselves'.format(message.author.id))
						return
					await message.channel.send('<:killed:690998665686548483>')
					await message.channel.send('<@{}> dealt {} damage, killing {}!'.format(message.author.id,'{:,}'.format(damage),messageParameter))
					storedStats[str(message.author.id)]['damage'] += damage
				else:
					await message.channel.send('You dealt {0} damage to {1}\n{1} has {2} HP remaining'.format('{:,}'.format(damage),messageParameter,'{:,}'.format((storedStats[str(targetUserID[1])]['hp']))))
					storedStats[str(message.author.id)]['damage'] += damage
			return
				
	if splitMessage[0] == '!roll':
		if len(splitMessage) == 2:
			await message.channel.send("<@{}> rolled a {}".format(message.author.id, random.randint(1, int(splitMessage[1]))))
		else:
			await message.channel.send("Type a space and a number after !roll to roll a dice that size")
		return

	
	if message.content.lower() == '!stats':
		if str(message.author.id) not in storedStats:
			storedStats[str(message.author.id)] = {'hp' : 50, 'damage' : 0, 'deaths' : 0}
		await message.channel.send('<@{}>\nHP: {}\nDamage Dealt: {}\nDeaths: {}'.format(str(message.author.id),'{:,}'.format(storedStats[str(message.author.id)]['hp']),'{:,}'.format(storedStats[str(message.author.id)]['damage']),'{:,}'.format(storedStats[str(message.author.id)]['deaths'])))
	
	if message.content.lower() == '!save' and (isAdmin == "true"):
		with open('attacks.json', 'w') as fp:
			json.dump(storedStats,fp)
		print("data saved to server")
		await message.channel.send("data saved to server")
	
	if message.content.lower() == '!load' and (isAdmin == "true"):
		jsonFile = open('attacks.json')
		jsonStr = jsonFile.read()
		storedStats = json.loads(jsonStr)
		print("save data loaded")
		await message.channel.send("save data loaded")
		
	if message.content.lower() == '!flip':
		if random.randint(1, 2) == 1:#heads
			await message.add_reaction('👧')#react heads
		else:
			await message.add_reaction('🐀')#react tails
		return

	
	if message.content.lower() == '!list':
		listedEmoji = ''#initializes the variable so that values can be 'added' into it
		for key in animatedEmoji:
			listedEmoji += '{} --> {}\n'.format(key,animatedEmoji[key])
		await message.channel.send(listedEmoji)
		return
	
	#The following searches the user's message to see if any of the custom emoji set matches
	#If it does then it will replace it, and resend the message on behalf of the user
	#	while also deleting the original users message
	#To identify the original user who sent the message, it also @'s them
	modifiedMessage = message.content
	switchFlag = 0 #A flag that determines of a match was made, and if the users message should be replaced
	for key in animatedEmoji:
		matchCheck = re.search(re.escape(key), message.content, flags=re.I)#Check if the message has a replacable emoji
		if (str(matchCheck) != "None"):
			modifiedMessage = re.sub(re.escape(key), animatedEmoji[key], modifiedMessage, flags=re.I)
			switchFlag = 1#sets a flag that a match was made, and should replace the message
	if  switchFlag == 1:#ONLY replace if a match was found
		await message.channel.send('<@{}>:'.format(message.author.id))
		await message.delete()
		await message.channel.send(modifiedMessage)
			



client.run(TOKEN)


