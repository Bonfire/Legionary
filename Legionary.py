import math
import platform
import requests
import discord
from discord.ext import commands
from lxml import html

# Discord Bot Token
from tokenFile import botToken

bot = commands.Bot(command_prefix="!")
bot.remove_command("help")

# List of members, list of roles, list of colors, and list of stat names
membersList = []
legionRoles = ['Recruit', 'Corporal', 'Sergeant', 'Lieutenant', 'Captain', 'General', 'General Emeritus', 'Owner']
legionColors = [0x99aab5, 0xf1c40f, 0xe67e22, 0x9b59b6, 0x992d22, 0x3498db, 0xad1457, 0x2ecc71]
statNames = ['Overall', 'Attack', 'Defence', 'Strength', 'Hitpoints', 'Ranged', 'Prayer', 'Magic', 'Cooking',
             'Woodcutting', 'Fletching', 'Fishing', 'Firemaking', 'Crafting', 'Smithing', 'Mining', 'Herblore',
             'Agility', 'Thieving', 'Slayer', 'Farming', 'Runecrafting', 'Hunter', 'Construction']

# Channel objects
logChannel = bot.get_channel(515702280063025171)
newsChannel = bot.get_channel(515684275580960769)
agreeChannel = bot.get_channel(515688016207937585)
botChannel = bot.get_channel(516433581992706058)

@bot.event
async def on_ready():
	"""
	Initializes the bot and displays relevant information
	Also populates the members list of dictionaries
	"""

	print('Logged in as {} (ID: {}) | Connected to {} servers | Connected to {} users'
	      .format(bot.user.name, bot.user.id, len(bot.guilds), len(set(bot.get_all_members()))))
	print('Current Discord.py Version: {} | Current Python Version: {}'
	      .format(discord.__version__, platform.python_version()))

	for server in bot.guilds:
		if server.name == "Lost Legion":
			for member in server.members:
				addMember(member)


@bot.command()
@commands.has_any_role('Captain', 'Owner', 'General', 'General Emeritus')
async def help(ctx, *args):
	commandsEmbed = discord.Embed(title="Legionary Bot Help - By Bonf", color=0xffea00)
	commandsEmbed.description = "Type !<command> to run a command!"
	commandsEmbed.add_field(name="!help",
	                        value='Shows this help message.',
	                        inline=False)
	commandsEmbed.add_field(name="!agree",
	                        value='Allows users to agree to the handbook.',
	                        inline=False)
	commandsEmbed.add_field(name="!recruit <name>",
	                        value='Manually recruits a user by name.',
	                        inline=False)
	commandsEmbed.add_field(name="!promote <name>",
	                        value='Manually promotes a user by name.',
	                        inline=False)
	commandsEmbed.add_field(name="!kick <name>",
	                        value='Kicks a user from the server.',
	                        inline=False)
	commandsEmbed.add_field(name="!names",
	                        value='Uploads the name of all current clan members.',
	                        inline=False)
	commandsEmbed.add_field(name="!stats <name>",
	                        value='Looks up that RSN\'s stats.',
	                        inline=False)
	commandsEmbed.add_field(name="!hcim <name>",
	                        value='Looks up that RSN\'s HCIM stats and sees if they\'re dead or alive',
	                        inline=False)
	commandsEmbed.set_footer(icon_url=ctx.author.avatar_url,
	                         text="Requested by <@!{}>".format(ctx.author.id))

	await ctx.message.channel.send(embed=commandsEmbed)
	await modLog("Help", "<@!{}> has requested the commands list".format(ctx.author.id), ctx)


def addMember(user: discord.User):
	"""Adds a new user to the members list"""

	newMember = {'name': user.display_name, 'id': user.id, 'role': user.top_role.name}
	membersList.append(dict(newMember))


def removeMember(user: discord.User):
	"""Searches the members list for a specific member and removes them"""

	for memberData in membersList:
		if memberData['name'] == user.display_name:
			membersList.remove(memberData)


async def modLog(eventName, eventDescription, *args):
	"""Logs any bot commands and actions to the proper channel"""
	modEmbed = discord.Embed(title='Moderation Log', color=0xffea00)
	modEmbed.add_field(name='Event: ' + eventName, value=eventDescription, inline=False)

	if len(args) > 0:
		modEmbed.add_field(name='Link', value='[Link to Message](https://discordapp.com/channels/{}/{}/{})'.format(
			args[0].message.guild.id, args[0].message.channel.id, args[0].message.id))
	await logChannel.send(embed=modEmbed)


@bot.event
async def on_member_join(user: discord.User):
	"""
	Sends new members a message regarding recruiting information
	Also adds them to the members list
	"""

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
	                           value="Type \"!agree\" in the <#515688016207937585> channel when you have changed your name and agree to The Handbook",
	                           inline=False)
	recruitmentEmbed.set_footer(text="Questions? Please contact the person who added you to our server or Bonf!")
	await user.send(embed=recruitmentEmbed)
	await modLog("Join", "<@!{}> has joined the server. A recruitment message has been sent.".format(user.id))
	addMember(user)


@bot.event
async def on_member_remove(user: discord.Member):
	"""Removes members who leave the server from the members list"""

	removeMember(user)
	await modLog("Leave", "{} (<@!{}>) has left the server".format(user.display_name, user.id))


@bot.event
async def on_member_update(oldUserInfo: discord.User, newUserInfo: discord.User):
	"""
	Updates member data in the members list
	Will update names, promotions, demotions, and recruitment
	"""

	if oldUserInfo.display_name != newUserInfo.display_name:
		if oldUserInfo.display_name != '@everyone':
			removeMember(oldUserInfo)
			addMember(oldUserInfo)
			await modLog("Name Change", "{} has changed their name to <@!{}>"
			             .format(oldUserInfo.display_name, newUserInfo.id))

	if oldUserInfo.top_role != newUserInfo.top_role:
		if oldUserInfo.top_role.name != '@everyone':
			removeMember(oldUserInfo)
			addMember(newUserInfo)
			await modLog("Rank Change", "<@!{}> had their rank changed from {} to {}"
			             .format(oldUserInfo.id, oldUserInfo.top_role.name, newUserInfo.top_role.name))


@bot.command()
async def agree(ctx):
	"""This will recruit new members once they've agreed to the handbook"""

	if ctx.channel == agreeChannel:
		recruitRoleID = discord.utils.get(ctx.guild.roles, name="Recruit")
		await ctx.author.add_roles(roles=recruitRoleID)
		await newsChannel.send("@everyone please welcome <@!%s> to the clan!" % ctx.author.id)
		await modLog("Agreement", "<@!{}> has agreed to the handbook"
		             .format(ctx.author.id), ctx)


@bot.command()
@commands.has_any_role('Captain', 'Owner', 'General', 'General Emeritus')
async def recruit(ctx, user: discord.User):
	"""This can be called to manually recruit new members"""

	recruitRoleID = discord.utils.get(ctx.guild.roles, name="Recruit")
	await user.add_roles(roles=recruitRoleID)
	await newsChannel.send("@everyone please welcome <@!%s> to the clan!" % user.id)


@bot.command()
@commands.has_any_role('Captain', 'Owner', 'General', 'General Emeritus')
async def promote(ctx, user: discord.User):
	"""This can be called to manually promote members"""

	currentRole = user.top_role
	if currentRole.name != 'Owner' and user.display_name != '@everyone':
		newRoleNumber = legionRoles.index(currentRole.name) + 1
		newRoleName = legionRoles[newRoleNumber]

		# Remove all roles and replace with the new one
		newRoleID = discord.utils.get(ctx.guild.roles, name=newRoleName)

		# Make sure we give the higher roles their moderator statuses
		if newRoleName == 'Lieutenant':
			modRoleID = discord.utils.get(ctx.guild.roles, name="Moderator")
			await user.edit(roles=[newRoleID, modRoleID])
		elif newRoleName == 'General' or newRoleName == 'Captain':
			globalRoleID = discord.utils.get(ctx.guild.roles, name="Global Moderator")
			await user.edit(roles=[newRoleID, globalRoleID])
		else:
			await user.edit(roles=[newRoleID])

		await newsChannel.send("<@!%s> has been promoted to %s!" % (user.id, newRoleName))

		await modLog("Promotion", "<@!{}> was promoted to {} by {}"
		             .format(user.id, user.top_role, ctx.author.display_name), ctx)


@bot.command()
@commands.has_any_role('Captain', 'Owner', 'General', 'General Emeritus')
async def kick(ctx, user: discord.User):
	"""This is used to remove players from the clan and members list"""

	removeMember(user)
	await user.kick()
	await modLog("Kick", "{} was removed from the server files and kicked"
	             .format(user.display_name), ctx)


@bot.command()
@commands.has_any_role('Captain', 'Owner', 'General', 'General Emeritus')
async def names(ctx):
	"""Will send a list of all current members in the discord"""

	with open("Names.txt", "w+") as namesFile:
		members = ctx.guild.members
		for person in members:
			if person.bot is False and person.top_role.name != "Guest" and person.top_role.name != "@everyone":
				namesFile.write(person.display_name + "\n")
	namesFile.close()
	await bot.send_file(ctx.channel, "./Names.txt")

	await modLog("Names", "<@!{}> has requested the names list"
	             .format(ctx.author.id), ctx)


@bot.command()
async def stats(ctx, *, message: str):
	"""Will display a list of a player's stats"""

	if ctx.channel == botChannel:
		hiscoreLookup = requests.get("https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player=" + message)
		separatedStats = hiscoreLookup.text.split("\n")

		statEmbed = discord.Embed(title="Stats for " + message, color=0x2ecc71)

		statDesc = "Stats for {}".format(message) + "\n (Level, XP) \n"
		for stat in range(0, 23):
			statName = statNames[stat]
			statLevel = separatedStats[stat].split(",")[1]
			statXP = separatedStats[stat].split(",")[2]
			statDesc += statName + ": " + statLevel + ", " + statXP + "\n"

		statEmbed.description = statDesc
		await ctx.channel.send(embed=statEmbed)
	else:
		await ctx.channel.send(
			"You can only run this command in {}".format(botChannel.mention))


@bot.command()
async def hcim(ctx, *, message: str):
	"""Will look up, add or remove HCIM player tracking"""

	if ctx.channel == botChannel:
		hcimLookup = requests.get(
			"https://secure.runescape.com/m=hiscore_oldschool_hardcore_ironman/index_lite.ws?player=" + message)
		separatedStats = hcimLookup.text.split("\n")
		overallScore = int(separatedStats[0].split(",")[0])
		skillTotal = int(separatedStats[0].split(",")[1])
		scorePageNum = math.ceil(overallScore / 25)

		scorePageHTML = requests.get(
			"https://secure.runescape.com/m=hiscore_oldschool_hardcore_ironman/overall.ws?table=0&page=" + str(
				scorePageNum)).content
		scorePageTree = html.fromstring(scorePageHTML)

		playerScores = scorePageTree.xpath(
			'//tr[@class="personal-hiscores__row personal-hiscores__row--dead"]/td[2]/a/text()')
		playerScores = [name.replace('\xa0', ' ') for name in playerScores]

		if message in playerScores:
			HCIMStatusEmbed = discord.Embed(title="HCIM Status for " + message, color=0xff0000)
			HCIMStatusEmbed.description = "Player is dead! Final skill total of " + str(skillTotal) + "\n"
			HCIMStatusEmbed.description += "[Link to Profile](https://secure.runescape.com/m=hiscore_oldschool_hardcore_ironman/hiscorepersonal.ws?user1=" + message.replace(
				" ", "%20") + ")"
			await ctx.channel.send(embed=HCIMStatusEmbed)
		else:
			HCIMStatusEmbed = discord.Embed(title="HCIM Status for " + message, color=0x00ff00)
			HCIMStatusEmbed.description = "Player is alive with a hiscore position of " + str(
				overallScore) + ", skill total of " + str(skillTotal) + "\n"
			HCIMStatusEmbed.description += "[Link to Profile](https://secure.runescape.com/m=hiscore_oldschool_hardcore_ironman/hiscorepersonal.ws?user1=" + message.replace(
				" ", "%20") + ")"
			await ctx.channel.send(embed=HCIMStatusEmbed)
	else:
		await ctx.channel.send(
			"You can only run this command in {}".format(botChannel.mention))


bot.run(botToken)
