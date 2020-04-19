#Code written by Tradam --> https://github.com/realtradam

import os

import discord
import random
import json
import re #regular expression
from mcstatus import MinecraftServer #Use 'python3 -m pip install mcstatus' to install, required for minecraft capabilities
from dotenv import load_dotenv #Substitues the API key variable

storedStats = {}
#{userid : {hp : num, damage : num, death: num}, etc.}

#The following are usef for emoji conversion, changes set depending on which server
#	is sending the message.
storedEmoji1 = {"<normal-emoji-on-server>": "<custom-animated-emoji>"}
#The first emoji set is set for a specific server of your choice
#You can set emojis on your server to be converted into emojis
#	of your choice(ones that are animated for example)
				
storedEmoji2 = {"!cheer": "<a:cheated:690837457440210945>", 
				"!stress": "<a:stressed:690851643863990302>",
				"!dance": "<a:dance:690853091704176660>",
				"🦜": "<a:partyparrot:691049985264975933>",
				"!trash": "<a:blobtrash:691090868123467866>",
				"!jojo": "<a:jotarodance:691090868513538048>",
				"!bongo": "<a:bongoowo:691090866965839912>"}
#The second emoji set will work on any server, but uses generic commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')# You need to set up a .env file which holds your token

client = discord.Client()

#Sets up the bot, its variables, etc. when the bot is initially run
@client.event
async def on_ready():
	global storedStats
	print('{} is connected to the following servers:'.format(client.user))
	for guild in client.guilds:
		print('\t- {} (id: {})'.format(guild.name,guild.id))
	await client.change_presence(status = 'None', activity=discord.Game('you like a damn fiddle'))
	
	#Loads up the statistics of players using the !attack command
	json1_file = open('attacks.json')
	json1_str = json1_file.read()
	storedStats = json.loads(json1_str)
	
	print("save data loaded")
	print('Bot is live!')
#            break

#Invoked whenever a message is sent in a server
@client.event
async def on_message(message):
	#Variable set up
	global storedStats, storedEmoji1, storedEmoji2
	temp = 0
	temp1 = 0
	temp2 = 0
	#Used for user identification
	isVerified = "false"
	isAdmin = "false"
	#Address to server
	mcServer = MinecraftServer("<server.ip>", <port>)
	
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
	if str(message.guild.id) == str("<server-id>"):
		animatedEmoji = storedEmoji1
	else: #All other servers use the generic set
		animatedEmoji = storedEmoji2
	
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
				os.system('(cd <path/to/folder>; ./<runnable-script>)')#Run a script that will correctly start your server
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
					with open ("<path/to/PID.txt>", "r") as myfile: #path to text file that stores the PID of the minecraft server, so that the server can be told to shut down
						pid = myfile.read()
					os.system("kill -15 {}".format(pid))
					await message.channel.send("Server has shut down")
			except ConnectionError:
				await message.channel.send("The server is already Offline (Or if you just booted it up, hasn't come Online yet)")
		else:
			await message.channel.send("You do not have permission to do that")
	
	#Splits the message, so the first word can be matched to a command, and use the rest of the words as parameters
	temp = message.content.lower().split()
	if (len(temp) == 2): #If the command has a parameter
		if (temp[0] == "!react") and (len(temp) == 2):
			for key in animatedEmoji:
				if temp[1] == key:
					await message.delete()
					async for react in message.channel.history(limit=1):
						await react.add_reaction(animatedEmoji[key])
						return
			return
		
		if (temp[0] == "!delete") and (len(temp) == 2) and (isAdmin == "true"):
			#This can be optimized by sending a batch delete rather then increment once
			#It's somehwere in the discord.py api
			async for delete in message.channel.history(limit=(int(temp[1])+1)):
				await delete.delete()
			return
		
		if (temp[0] == '!attack') and (len(temp) == 2):
			#A little game where users can attack eachother
			#These variable names NEED to be cleaned up
			temp1 = temp[1]
			temp2 = [temp1[:2],temp1[2:-1],temp1[-1:]]
			if temp2[1][:1] == '!':
				temp2[1] = temp2[1][1:]
			if temp2[0] == '<@' and temp2[2] == '>':
				temp = random.randint(1,29)
				if str(message.author.id) not in storedStats:
					storedStats[str(message.author.id)] = {'hp' : 50, 'damage' : 0, 'deaths' : 0}
				if str(temp2[1]) == "<id-of-this-bot>":
					await message.channel.send('<a:angryAwooGlitch:691087516819914772>')
					return
				elif str(temp2[1]) not in storedStats:
					storedStats[str(temp2[1])] = {'hp' : 50, 'damage' : 0, 'deaths' : 0}
				
				storedStats[str(temp2[1])]['hp'] -= temp
				if storedStats[str(temp2[1])]['hp'] <= 0:
					storedStats[str(temp2[1])]['deaths'] += 1
					storedStats[str(temp2[1])]['hp'] = 50
					if str(message.author.id) == str(temp2[1]):
						await message.channel.send('<a:blobhang:691023822576549930>')
						await message.channel.send('<@{}> killed themselves'.format(message.author.id))
						return
					await message.channel.send('<:killed:690998665686548483>')
					await message.channel.send('<@{}> dealt {} damage, killing {}!'.format(message.author.id,'{:,}'.format(temp),temp1))
					storedStats[str(message.author.id)]['damage'] += temp
				else:
					await message.channel.send('You dealt {0} damage to {1}\n{1} has {2} HP remaining'.format('{:,}'.format(temp),temp1,'{:,}'.format((storedStats[str(temp2[1])]['hp']))))
					storedStats[str(message.author.id)]['damage'] += temp
			return
				
		if temp[0] == '!roll':
			if len(temp) > 1:
				await message.channel.send("<@{}> rolled a {}".format(message.author.id, random.randint(1, int(temp[1]))))
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
		json1_file = open('attacks.json')
		json1_str = json1_file.read()
		storedStats = json.loads(json1_str)
		print("save data loaded")
		await message.channel.send("save data loaded")
		
	if message.content.lower() == '!flip':
		if random.randint(1, 2) == 1:#heads
			await message.add_reaction('👧')#react heads
		else:
			await message.add_reaction('🐀')#react tails
		return

	
	if message.content.lower() == '!list':
		temp = ""
		for key in animatedEmoji:
			temp += '{} --> {}\n'.format(key,animatedEmoji[key])
		await message.channel.send(temp)
		return
	
	#The following searches the user's message to see if any of the custom emoji set matches
	#If it does then it will replace it, and resend the message on behalf of the user
	#	while also deleting the original users message
	#To identify the original user who sent the message, it also @'s them
	temp2 = message.content
	switchFlag = 0
	for key in animatedEmoji:
		temp = re.search(re.escape(key), message.content, flags=re.I)
		if (str(temp) != "None"):
			temp2 = re.sub(re.escape(key), animatedEmoji[key], temp2, flags=re.I)
			switchFlag = 1#sets a flag that a match was made, and should replace the message
	if  switchFlag == 1:#ONLY replace if a match was found
		await message.channel.send('<@{}>:'.format(message.author.id))
		await message.delete()
		await message.channel.send(temp2)
		



client.run(TOKEN)


