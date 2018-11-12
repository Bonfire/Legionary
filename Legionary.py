# For Legion Discord Bot
import discord
import asyncio
import platform
from discord.ext import commands

# Other Libraries
import datetime
import json

# Discord Bot Token
from tokenFile import botToken

bot = commands.Bot(command_prefix="!")
bot.remove_command("help")

# Talk Channel ID
talkID = '463477926961348643'
talkChannel = bot.get_channel(talkID)

legionRoles = ['Recruit', 'Corporal', 'Sergeant', 'Lieutenant', 'Captain', 'General', 'Owner']
legionColors = [0x99aab5, 0xf1c40f, 0xe67e22, 0x9b59b6, 0x992d22, 0x3498db, 0x2ecc71]
membersMessages = ['', '', '', '', '', '', '']


async def removeFromFiles(topRole, memberName):
	with open('Members.json', "r") as membersFile:
		membersList = json.load(membersFile)

	del membersList[topRole.name][memberName]

	with open('Members.json', "w") as membersFile:
		json.dump(membersList, membersFile, indent=2, sort_keys=True)


async def modLog(eventName, eventDescription, *args):
	# Mod Channel ID
	logID = '511391715027058728'
	logChannel = bot.get_channel(logID)

	modEmbed = discord.Embed(title='Moderation Log', color=0xffea00)
	modEmbed.add_field(name='Event: ' + eventName, value=eventDescription, inline=False)

	if (len(args) > 0):
		modEmbed.add_field(name='Link', value='[Link to Message](https://discordapp.com/channels/{}/{}/{})'.format(
			args[0].message.server.id, args[0].message.channel.id, args[0].message.id))
	await bot.send_message(logChannel, embed=modEmbed)


@bot.event
async def on_ready():
	print('Logged in as ' + bot.user.name + ' (ID:' + bot.user.id + ') | Connected to ' + str(
		len(bot.servers)) + ' servers | Connected to ' + str(len(set(bot.get_all_members()))) + ' users')
	print('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__,
	                                                                           platform.python_version()))


@bot.event
async def on_member_join(user: discord.Member):
	recruitmentEmbed = discord.Embed(title="Recruitment to OS Lost Legion", color=0xffea00)
	recruitmentEmbed.description = "Thank you for showing interest in joining OS Lost Legion!\nI am a bot that will help walk you through the recruitment process\nPlease follow these steps to join:"

	recruitmentEmbed.add_field(name="1. Read The Handbook",
	                           value="Please view The Handbook located on the <#468933726894555136> channel",
	                           inline=False)
	recruitmentEmbed.add_field(name="2. Read The Requirements",
	                           value="Read and adhere to the requirements located on The Handbook", inline=False)
	recruitmentEmbed.add_field(name="3. Change Your Name",
	                           value="Verify that you have changed your name on the server to your in-game name",
	                           inline=False)
	recruitmentEmbed.add_field(name="4. Agree to The Handbook",
	                           value="Type \"!agree\" in the <#511061051476017152> channel when you have changed your name and agree to The Handbook",
	                           inline=False)
	recruitmentEmbed.set_footer(text="Questions? Please contact the person who added you to our discord server!")
	await bot.send_message(user, embed=recruitmentEmbed)
	await modLog("Join",
	             "<@!{}> has joined the server. A recruitment message has been sent.".format(user.id))


@bot.event
async def on_member_remove(user: discord.Member):
	with open('Members.json', "r") as membersFile:
		membersList = json.load(membersFile)

	with open('Members.json', "w") as membersFile:
		del membersList[user.top_role.name][user.display_name]
		json.dump(membersList, membersFile, indent=2, sort_keys=True)

	await modLog("Leave", "<@!{}> has left the server".format(user.id))


@bot.event
async def on_member_update(oldInfo: discord.Member, newInfo: discord.Member):
	if oldInfo.display_name != newInfo.display_name:
		with open('Members.json', "r") as membersFile:
			membersList = json.load(membersFile)

		with open('Members.json', "w") as membersFile:
			lastDate = membersList[oldInfo.top_role.name][oldInfo.display_name]['date']
			del membersList[oldInfo.top_role.name][oldInfo.display_name]
			membersList[newInfo.top_role.name][newInfo.display_name] = {"id": newInfo.id, "date": lastDate}
			json.dump(membersList, membersFile, indent=2, sort_keys=True)

		await modLog("Name Change",
		             "{} has changed their name to <@!{}>".format(oldInfo.display_name, newInfo.id))

	# This will handle all promotions, demotions, and recruitments
	if oldInfo.top_role != newInfo.top_role:
		with open('Members.json', "r") as membersFile:
			membersList = json.load(membersFile)

		with open('Members.json', "w") as membersFile:
			del membersList[oldInfo.top_role.name][oldInfo.display_name]
			membersList[newInfo.top_role.name][newInfo.display_name] = {"id": newInfo.id,
			                                                            "date": datetime.datetime.today().strftime(
				                                                            '%m/%d/%Y')}
			json.dump(membersList, membersFile, indent=2, sort_keys=True)

		await modLog("Rank Change",
		             "<@!{}> had their rank changed from {} to {}".format(oldInfo.id, oldInfo.top_role.name,
		                                                                  newInfo.top_role.name))


@bot.command(pass_context=True)
@commands.has_any_role('Captain', 'Owner', 'General')
async def help(ctx, *args):
	commandsEmbed = discord.Embed(title="Legionary Bot Help - By Bonf", color=0xffea00)
	commandsEmbed.description = "Type !<command> to run a command!"
	commandsEmbed.add_field(name="!members [update]",
	                        value='Lists all current members.\n[update] - Updates the previous members list',
	                        inline=False)
	commandsEmbed.add_field(name="!agree",
	                        value='Agrees to The Handbook and recruits the user',
	                        inline=False)
	commandsEmbed.add_field(name="!names",
	                        value='Creates and sends a file containing all member names',
	                        inline=False)
	commandsEmbed.add_field(name="!recruit <name>", value='Recruits <name> to the clan', inline=False)
	commandsEmbed.add_field(name="!promote <name>",
	                        value='Promotes <name> one rank higher (must already be recruited)', inline=False)
	commandsEmbed.add_field(name="!remove <name>",
	                        value='Removes <name> from the server files', inline=False)
	commandsEmbed.add_field(name="!kick <name>",
	                        value='Kicks <name> from the clan (discord and server files)', inline=False)

	commandsEmbed.set_footer(icon_url=ctx.message.author.avatar_url,
	                         text="Requested by <@!{}>".format(ctx.message.author.id))

	await bot.send_message(ctx.message.channel, embed=commandsEmbed)
	await modLog("Help",
	             "<@!{}> has requested the commands list".format(ctx.message.author.id), ctx)


@bot.command(pass_context=True)
async def agree(ctx):
	newsID = '463472622127284234'
	newsChannel = bot.get_channel(newsID)
	if ctx.message.channel.name == 'agree':
		recruitRoleID = discord.utils.get(ctx.message.server.roles, name="Recruit")
		await bot.add_roles(ctx.message.author, recruitRoleID)
		await bot.send_message(newsChannel,
		                       "@everyone please welcome <@!%s> to the clan!" % ctx.message.author.id)

		await modLog("Agreement",
		             "<@!{}> has agreed to the handbook".format(ctx.message.author.id), ctx)


@bot.command(pass_context=True)
@commands.has_any_role('Captain', 'Owner', 'General')
async def recruit(ctx, user: discord.Member):
	newsID = '463472622127284234'
	newsChannel = bot.get_channel(newsID)
	recruitRoleID = discord.utils.get(ctx.message.server.roles, name="Recruit")
	await bot.add_roles(user.id, recruitRoleID)
	await bot.send_message(newsChannel, "@everyone please welcome <@!%s> to the clan!" % user.id)


@bot.command(pass_context=True)
@commands.has_any_role('Captain', 'Owner', 'General')
async def promote(ctx, user: discord.Member):
	newsID = '463472622127284234'
	newsChannel = bot.get_channel(newsID)
	currentRole = user.top_role
	if currentRole.name != 'Owner' and user.display_name != '@everyone':
		newRoleNumber = legionRoles.index(currentRole.name) + 1
		newRoleName = legionRoles[newRoleNumber]

		# Remove all roles and replace with the new one
		newRoleID = discord.utils.get(ctx.message.server.roles, name=newRoleName)

		# Make sure we give the higher roles their moderator statuses
		if newRoleName == 'Lieutenant' or newRoleName == 'Captain':
			modRoleID = discord.utils.get(ctx.message.server.roles, name="Moderator")
			await bot.replace_roles(user, newRoleID, modRoleID)
		elif newRoleName == 'General':
			globalRoleID = discord.utils.get(ctx.message.server.roles, name="Global Moderator")
			await bot.replace_roles(user, newRoleID, globalRoleID)
		else:
			await bot.replace_roles(user, newRoleID)

		await bot.send_message(newsChannel,
		                       "<@!%s> has been promoted to %s!" % (user.id, newRoleName))

		await modLog("Promotion",
		             "<@!{}> was promoted to {} by {}".format(user.id, user.top_role,
		                                                      ctx.message.author.display_name), ctx)


@bot.command(pass_context=True)
@commands.has_any_role('Captain', 'Owner', 'General')
async def remove(ctx, user: discord.Member):
	# Remove the player from the files
	await removeFromFiles(user.top_role, user.display_name)
	await modLog("Remove",
	             "{} was removed from the server files".format(user.display_name), ctx)


@bot.command(pass_context=True)
@commands.has_any_role('Captain', 'Owner', 'General')
async def kick(ctx, user: discord.Member):
	# Remove the player from the files
	await removeFromFiles(user.top_role, user.display_name)

	# Kick the player from the clan
	await bot.kick(user)
	await modLog("Kick",
	             "{} was removed from the server files and kicked".format(user.display_name), ctx)


@bot.command(pass_context=True)
@commands.has_any_role('Captain', 'Owner', 'General')
async def members(ctx, *args):
	# If they want to update, get rid of the older messages
	if args == "update":
		for index, message in enumerate(membersMessages):
			await bot.delete_message(membersMessages[index])

	with open('Members.json', "r") as membersFile:
		membersList = json.load(membersFile)

	for index, rank in enumerate(membersList):
		# The title of the embed is the rank name, the color is the index of colors at the rank name
		rankEmbed = discord.Embed(title=rank, color=legionColors[legionRoles.index(rank)])
		rankDesc = ""

		for member in membersList[rank]:
			rankDesc += (member + "  -  " + membersList[rank][member]['date'] + "\n")

		rankEmbed.description = rankDesc
		membersMessages[index] = await bot.send_message(ctx.message.channel, embed=rankEmbed)

	await modLog("Members List",
	             "<@!{}> has requested the members list".format(ctx.message.author.id), ctx)


@bot.command(pass_context=True)
@commands.has_any_role('Captain', 'Owner', 'General')
async def names(ctx):
	with open('Members.json', "r") as membersFile:
		membersList = json.load(membersFile)

		with open("Names.txt", "w+") as namesFile:
			for rank in membersList:
				for member in membersList[rank]:
					print(member['name'])
					namesFile.write(member['name'] + "\n")
		namesFile.close()
		await bot.send_file(ctx.message.channel, "./Names.txt")

		await modLog("Names",
		             "<@!{}> has requested the names list".format(ctx.message.author.id), ctx)


bot.run(botToken)
