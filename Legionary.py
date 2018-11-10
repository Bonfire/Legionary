# For Legion Discord Bot
import discord
import asyncio
import platform
from discord.ext import commands

# Other Libraries
import datetime
import re
import json

# Discord Bot Token
from tokenFile import botToken

bot = commands.Bot(command_prefix="!")

# News Channel ID
newsID = '463472622127284234'

# Talk Channel ID
talkID = '463477926961348643'

legionRoles = ['Recruit', 'Corporal', 'Sergeant', 'Lieutenant', 'Captain', 'General', 'Owner']
legionColors = [0x99aab5, 0xf1c40f, 0xe67e22, 0x9b59b6, 0x992d22, 0x3498db, 0x2ecc71]
membersMessages = ['', '', '', '', '', '', '']


@bot.event
async def on_ready():
	print('Logged in as ' + bot.user.name + ' (ID:' + bot.user.id + ') | Connected to ' + str(
		len(bot.servers)) + ' servers | Connected to ' + str(len(set(bot.get_all_members()))) + ' users')
	print('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__,
	                                                                           platform.python_version()))


@bot.event
async def on_message(ctx):
	# Only allow the staff to use these commands
	authorRoles = [role.name for role in ctx.author.roles]
	if 'Captain' in authorRoles or 'General' in authorRoles or 'Owner' in authorRoles:
		# Process everything else as a command
		await bot.process_commands(ctx)


@bot.command(pass_context=True)
async def commands(ctx, *args):
	commandsEmbed = discord.Embed(title="Legionary Bot Help - By Bonf", color=0xffea00)
	commandsEmbed.description = "Type !<command> to run a command!"
	commandsEmbed.add_field(name="!members [update]",
	                        value='Lists all current members.\n[update] - Updates the previous members list',
	                        inline=False)
	commandsEmbed.add_field(name="!recruit <name>", value='Recruits <name> to the clan', inline=False)
	commandsEmbed.add_field(name="!promote <name>",
	                        value='Promotes <name> one rank higher (must already be recruited)', inline=False)
	commandsEmbed.add_field(name="!remove <name>",
	                        value='Removes <name> from the server files', inline=False)
	commandsEmbed.add_field(name="!kick <name>",
	                        value='Kicks <name> from the clan (discord and server files)', inline=False)

	commandsEmbed.set_footer(icon_url=ctx.message.author.avatar_url,
	                         text="Requested by {}#{} ({})".format(ctx.message.author.name,
	                                                               ctx.message.author.discriminator,
	                                                               ctx.message.author.id))

	await bot.send_message(ctx.message.channel, embed=commandsEmbed)


@bot.command(pass_context=True)
async def recruit(ctx, user: discord.Member):
	recruitName = user.display_name
	recruitDate = datetime.datetime.today().strftime('%m/%d/%Y')

	print("[Recruiting] Recruiting " + user.display_name)

	roleID = discord.utils.get(user.server.roles, name="Recruit")
	await bot.add_roles(user, roleID)

	# Add their name to the members file
	membersFile = open('Members', 'a')
	membersFile.write("\n" + "Recruit" + "\t" + recruitName + "\t" + recruitDate)
	membersFile.close()

	await bot.send_message(ctx.message.channel,
	                       "@everyone please welcome <@!%s> to the clan!" % user.id)


@bot.command(pass_context=True)
async def promote(ctx, user: discord.Member):
	currentRole = user.top_role
	if currentRole.name != 'Owner' and user.display_name != '@everyone':
		newRoleNumber = legionRoles.index(currentRole.name) + 1
		newRoleName = legionRoles[newRoleNumber]

		# Remove all roles and replace with the new one
		newRoleID = discord.utils.get(ctx.message.server.roles, name=newRoleName)
		moderatorRoleID = discord.utils.get(ctx.message.server.roles, name="Moderator")
		globalModRoleID = discord.utils.get(ctx.message.server.roles, name="Global Moderator")

		# Make sure we give the higher roles their moderator statuses
		if newRoleName == 'Lieutenant' or newRoleName == 'Captain':
			await bot.replace_roles(user, newRoleID, moderatorRoleID)
		elif newRoleName == 'General':
			await bot.replace_roles(user, newRoleID, globalModRoleID)
		else:
			await bot.replace_roles(user, newRoleID)

		with open('Members.json', "r") as membersFile:
			membersList = json.load(membersFile)

		del membersList[currentRole.name][user.display_name]
		membersList[newRoleName][user.display_name] = {"date": datetime.datetime.today().strftime('%m/%d/%Y')}

		with open('Members.json', "w") as membersFile:
			json.dump(membersList, membersFile, indent=2, sort_keys=True)

		print("[Promotion] Promoted " + user.display_name + " to " + newRoleName)

		await bot.send_message(ctx.message.channel,
		                       "<@!%s> has been promoted to %s!" % (user.id, newRoleName))


async def removeFromFiles(memberName):
	# Find their name in the members list
	membersFile = open('Members', "r")
	lines = membersFile.readlines()
	membersFile.close()

	# Write every line down except for theirs (exclude their name, thus removing it)
	membersFile = open('Members', "w")
	for line in lines:
		if memberName not in line:
			membersFile.write(line)
	membersFile.close()


@bot.command(pass_context=True)
async def remove(ctx, user: discord.Member):
	# Remove the player from the files
	await removeFromFiles(user.display_name)
	await bot.send_message(ctx.message.channel, "%s has been removed from the files!" % user.display_name)


@bot.command(pass_context=True)
async def kick(ctx, user: discord.Member):
	# Remove the player from the files
	await removeFromFiles(user.display_name)

	# Kick the player from the clan
	await bot.kick(user)
	await bot.send_message(ctx.message.channel, "<@!%s> has been kicked from the clan!" % user)


@bot.command(pass_context=True)
async def members(ctx, *args):
	# The best way I could think of doing this. I know I can make it better...

	# If they want to update, get rid of the older messages
	if args == "update":
		for index, message in enumerate(membersMessages):
			await bot.delete_message(membersMessages[index])

	for index, rank in enumerate(legionRoles):
		membersFile = open('Members', 'r')

		# The title of the embed is the rank name, the color is the index of colors at the rank name
		rankEmbed = discord.Embed(title=rank, color=legionColors[legionRoles.index(rank)])
		rankDesc = ""

		membersLines = membersFile.readlines()

		for line in membersLines:
			# Split the line by tabs to get the rank, name, and date
			lineSplit = re.split(r'\t+', line)

			# Strip (chomp in perl) the last line for the newline character
			memberRank = lineSplit[0]
			memberName = lineSplit[1]
			memberDate = lineSplit[2].rstrip()

			# We go through each rank, rank by rank and make an embed out of it
			if memberRank == rank:
				rankDesc += (memberName + "\t" + memberDate + "\n")
		membersFile.close()

		rankEmbed.description = rankDesc
		membersMessages[index] = await bot.send_message(ctx.message.channel, embed=rankEmbed)


bot.run(botToken)
