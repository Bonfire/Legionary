import asyncio
import json
import os
import platform
from datetime import datetime

import aiohttp
import discord
import math
from discord.ext import commands
from fuzzywuzzy import fuzz
from lxml import html

# Discord Bot Token
from tokenFile import legionToken

bot = commands.Bot(command_prefix="!")
bot.remove_command("help")

# List of members, list of roles, list of colors, and list of stat names
membersList = []
legionRoles = ['Recruit', 'Corporal', 'Sergeant', 'Lieutenant', 'Captain', 'General', 'General Emeritus', 'Leader']
legionColors = [0x99aab5, 0xf1c40f, 0xe67e22, 0x9b59b6, 0x992d22, 0x3498db, 0xad1457, 0x2ecc71]
statNames = ['Overall', 'Attack', 'Defence', 'Strength', 'Hitpoints', 'Ranged', 'Prayer', 'Magic', 'Cooking',
             'Woodcutting', 'Fletching', 'Fishing', 'Firemaking', 'Crafting', 'Smithing', 'Mining', 'Herblore',
             'Agility', 'Thieving', 'Slayer', 'Farming', 'Runecrafting', 'Hunter', 'Construction']


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

	bot.logChannel = bot.get_channel(515702280063025171)
	bot.newsChannel = bot.get_channel(515684275580960769)
	bot.agreeChannel = bot.get_channel(515688016207937585)
	bot.pollsChannel = bot.get_channel(654476005926371328)


@bot.command()
async def help(ctx, *args):
	commandsEmbed = discord.Embed(title="Legionary Bot Help - By Bonf", color=0xffea00)
	commandsEmbed.description = "Type !<command> to run a command!"
	commandsEmbed.add_field(name="!help",
	                        value='Shows this help message.',
	                        inline=False)
	commandsEmbed.add_field(name="!agree <name>",
	                        value='Allows users to agree to the handbook and refer <name>.',
	                        inline=False)
	commandsEmbed.add_field(name="!recruit <discord name>",
	                        value='Manually recruits a user by name. (Captain+)',
	                        inline=False)
	commandsEmbed.add_field(name="!promote <discord name>",
	                        value='Manually promotes a user by name. (Captain+)',
	                        inline=False)
	commandsEmbed.add_field(name="!kick <discord name>",
	                        value='Kicks a user from the server. (Captain+)',
	                        inline=False)
	commandsEmbed.add_field(name="!names",
	                        value='Uploads the name of all current clan members. (Captain+)',
	                        inline=False)
	commandsEmbed.add_field(name="!ranks",
	                        value='Uploads the name of all current clan members, their ranks, and join date. (Captain+)',
	                        inline=False)
	commandsEmbed.add_field(name="!stats <runescape name>",
	                        value='Looks up that RSN\'s stats.',
	                        inline=False)
	commandsEmbed.add_field(name="!hcim <runescape name>",
	                        value='Looks up that RSN\'s HCIM stats and sees if they\'re dead or alive (btw)',
	                        inline=False)
	commandsEmbed.add_field(name="!price <item name>",
	                        value='Does a price lookup on the input item.',
	                        inline=False)
	commandsEmbed.set_footer(icon_url=ctx.author.avatar_url,
	                         text="Requested by {} (ID: {})".format(ctx.author.display_name, ctx.author.id))

	await ctx.message.channel.send(embed=commandsEmbed)
	await modLog("Help", "<@!{}> has requested the commands list".format(ctx.author.id), ctx)


def addMember(member: discord.Member):
	"""Adds a new user to the members list"""

	newMember = {'name': member.display_name, 'id': member.id, 'role': member.top_role.name}
	membersList.append(dict(newMember))


def removeMember(member: discord.Member):
	"""Searches the members list for a specific member and removes them"""

	for memberData in membersList:
		if memberData['name'] == member.display_name:
			membersList.remove(memberData)


async def modLog(eventName, eventDescription, *args):
	"""Logs any bot commands and actions to the proper channel"""
	modEmbed = discord.Embed(title='Moderation Log', color=0xffea00)
	modEmbed.add_field(name='Event: ' + eventName, value=eventDescription, inline=False)

	if len(args) > 0:
		modEmbed.add_field(name='Link', value='[Link to Message](https://discordapp.com/channels/{}/{}/{})'.format(
			args[0].message.guild.id, args[0].message.channel.id, args[0].message.id))
	await bot.logChannel.send(embed=modEmbed)


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
	                           value="Type `!agree @name RSN` (where `name` is the Discord tag of the member who referred you, and `RSN` is your in-game name) in the <#515688016207937585> channel. Do this when you have changed your name and agree to The Handbook.",
	                           inline=False)
	recruitmentEmbed.set_footer(text="Questions? Please contact the person who added you to our server or Bonf!")
	await user.send(embed=recruitmentEmbed)
	await modLog("Join",
	             "{} (ID: {}) has joined the server. A recruitment message has been sent.".format(user.display_name,
	                                                                                              user.id))
	addMember(user)


@bot.event
async def on_member_remove(member: discord.Member):
	"""Removes members who leave the server from the members list"""

	removeMember(member)
	await modLog("Leave", "{} (<@!{}>) has left the server".format(member.display_name, member.id))


@bot.event
async def on_member_update(oldMemberInfo: discord.Member, newMemberInfo: discord.Member):
	"""
	Updates member data in the members list
	Will update names, promotions, demotions, and recruitment
	"""

	if oldMemberInfo.display_name != newMemberInfo.display_name:
		if oldMemberInfo.display_name != '@everyone':
			removeMember(oldMemberInfo)
			addMember(oldMemberInfo)
			await modLog("Name Change", "{} has changed their name to <@!{}>"
			             .format(oldMemberInfo.display_name, newMemberInfo.id))

	if oldMemberInfo.top_role != newMemberInfo.top_role:
		if oldMemberInfo.top_role.name != '@everyone':
			removeMember(oldMemberInfo)
			addMember(newMemberInfo)
			await modLog("Rank Change", "<@!{}> had their rank changed from {} to {}"
			             .format(oldMemberInfo.id, oldMemberInfo.top_role.name, newMemberInfo.top_role.name))


async def anniversaryCheck():
	while True:
		await bot.wait_until_ready()

		for server in bot.guilds:
			if server.name == "Lost Legion":
				bot.newsChannel = bot.get_channel(515684275580960769)
				oneMonthRoleID = discord.utils.get(server.roles, name="1 Month")
				threeMonthsRoleID = discord.utils.get(server.roles, name="3 Months")
				sixMonthsRoleID = discord.utils.get(server.roles, name="6 Months")
				oneYearRoleID = discord.utils.get(server.roles, name="1 Year")

				members = server.members
				currentDateTime = datetime.today()
				for member in members:
					memberJoinDate = member.joined_at
					timeDelta = abs(currentDateTime - memberJoinDate)
					daysSinceJoining = timeDelta.days

					if (daysSinceJoining == 30):
						await member.add_roles(oneMonthRoleID)
					elif (daysSinceJoining == 90):
						await bot.newsChannel.send(
							"[Anniversary] Today is <@!{}>'s 3 month Lost Legion anniversary! Wish them a happy anniversary!".format(
								member.id))
						if (oneMonthRoleID in member.roles):
							await member.remove_roles(oneMonthRoleID)
						await member.add_roles(threeMonthsRoleID)
					elif (daysSinceJoining == 180):
						await bot.newsChannel.send(
							"[Anniversary] Today is <@!{}>'s 6 month Lost Legion anniversary! Wish them a happy anniversary!".format(
								member.id))
						if (threeMonthsRoleID in member.roles):
							await member.remove_roles(threeMonthsRoleID)
						await member.add_roles(sixMonthsRoleID)
					elif (daysSinceJoining == 360):
						await bot.newsChannel.send(
							"[Anniversary] Today is <@!{}>'s 1 year Lost Legion anniversary! Wish them a happy anniversary!".format(
								member.id))
						if (sixMonthsRoleID in member.roles):
							await member.remove_roles(sixMonthsRoleID)
						await member.add_roles(oneYearRoleID)
		await asyncio.sleep(86400)  # Task runs once a day


@bot.command()
async def agree(ctx, member: discord.Member, *RSN):
	"""This will recruit new members once they've agreed to the handbook"""

	if ctx.channel == bot.agreeChannel:
		if member is not None \
				and member.top_role.name is not "@everyone" \
				and member.top_role.name is not "@here" \
				and member is not ctx.author \
				and RSN is not None:
			joinedName = " ".join(RSN)
			strippedName = joinedName.strip()
			recruitRoleID = discord.utils.get(ctx.guild.roles, name="Recruit")
			await ctx.author.edit(nick=strippedName)
			await ctx.author.add_roles(recruitRoleID)
			await bot.newsChannel.send(
				"@everyone please welcome <@!{}> to the clan, referred by <@!{}>! Their RSN is {}".format(ctx.author.id, member.id, strippedName))
			await modLog("Agreement", "<@!{}> has agreed to the handbook, referred by {} with RSN {}"
			             .format(ctx.author.id, member.display_name, strippedName), ctx)
		else:
			await ctx.channel.send(
				"Please be sure to mention the person that _referred you_ and your RSN when agreeing. An example of this would be `!agree @Bonf#7654 MyName`, where `@Bonf#7654` is the person who referred you and `MyName` is your in-game name.")


@agree.error
async def agree_error(ctx, error):
	if isinstance(error, commands.BadArgument):
		await ctx.channel.send(
			"Please be sure to mention the person that _referred you_ and your RSN when agreeing. An example of this would be `!agree @Bonf#7654 MyName`, where `@Bonf#7654` is the person who referred you and `MyName` is your in-game name.")
		return

	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.channel.send(
			"Please be sure to mention the person that _referred you_ and your RSN when agreeing. An example of this would be `!agree @Bonf#7654 MyName`, where `@Bonf#7654` is the person who referred you and `MyName` is your in-game name.")
		return


@bot.command()
@commands.has_any_role('Captain', 'Leader', 'General', 'General Emeritus')
async def recruit(ctx, member: discord.Member):
	"""This can be called to manually recruit new members"""

	recruitRoleID = discord.utils.get(ctx.guild.roles, name="Recruit")
	await member.add_roles(recruitRoleID)
	await bot.newsChannel.send("@everyone please welcome <@!%s> to the clan!" % member.id)


@bot.command()
@commands.has_any_role('Captain', 'Leader', 'General', 'General Emeritus')
async def promote(ctx, member: discord.Member):
	"""This can be called to manually promote members"""

	currentRole = member.top_role
	if currentRole.name != 'Owner' and member.display_name != '@everyone':
		newRoleNumber = legionRoles.index(currentRole.name) + 1
		newRoleName = legionRoles[newRoleNumber]

		# Remove all roles and replace with the new one
		newRoleID = discord.utils.get(ctx.guild.roles, name=newRoleName)

		# Make sure we give the higher roles their moderator statuses
		if newRoleName == 'Lieutenant':
			modRoleID = discord.utils.get(ctx.guild.roles, name="Leadership")
			await member.edit(roles=[newRoleID, modRoleID])
		elif newRoleName == 'General' or newRoleName == 'Captain' or newRoleName == 'General Emeritus':
			globalRoleID = discord.utils.get(ctx.guild.roles, name="Staff")
			await member.edit(roles=[newRoleID, globalRoleID])
		else:
			await member.edit(roles=[newRoleID])

		await bot.newsChannel.send("<@!%s> has been promoted to %s!" % (member.id, newRoleName))

		await modLog("Promotion", "<@!{}> was promoted to {} by {}"
		             .format(member.id, member.top_role, ctx.author.display_name), ctx)


@bot.command()
@commands.has_any_role('Captain', 'Leader', 'General', 'General Emeritus')
async def kick(ctx, member: discord.Member):
	"""This is used to remove players from the clan and members list"""

	removeMember(member)
	await member.kick()
	await modLog("Kick", "{} was removed from the server files and kicked"
	             .format(member.display_name), ctx)


@bot.command()
@commands.has_any_role('Captain', 'Leader', 'General', 'General Emeritus')
async def names(ctx):
	"""Will send a list of all current members in the discord"""

	with open("Names.txt", "w+") as namesFile:
		members = ctx.guild.members
		for person in members:
			if person.bot is False and person.top_role.name != "Guest" and person.top_role.name != "@everyone":
				namesFile.write(person.display_name + "\n")
	namesFile.close()
	await ctx.message.channel.send(file=discord.File("Names.txt"))
	os.remove("Names.txt")

	await modLog("Names", "<@!{}> has requested the names list".format(ctx.author.id), ctx)


@bot.command()
@commands.has_any_role('Captain', 'Leader', 'General', 'General Emeritus')
async def ranks(ctx):
	"""Will send a list of all current members and their ranks"""

	with open("Ranks.txt", "w+") as ranksFile:
		roles = ctx.guild.roles
		members = ctx.guild.members
		for role in roles:
			if role.name is not "Guest" and role.name != "@everyone":
				for member in members:
					if member.top_role == role and member.bot is False:
						ranksFile.write(
							"{:<20} {:^20} {:>20}\n".format(member.display_name, role.name, str(member.joined_at)))
	ranksFile.close()
	await ctx.message.channel.send(file=discord.File("Ranks.txt"))
	os.remove("Ranks.txt")

	await modLog("Ranks", "<@!{}> has requested the ranks list".format(ctx.author.id), ctx)


@bot.command()
async def stats(ctx, *, message: str):
	"""Will display a list of a player's stats"""

	async with aiohttp.ClientSession() as session:
		async with session.get(
				"https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player=" + message) as hiscoreLookup:
			separatedStats = (await hiscoreLookup.text()).split("\n")

		statEmbed = discord.Embed(title="Stats for " + message, color=0x2ecc71)

		statDesc = "Stats for {}".format(message) + "\n (Level, XP) \n"
		for stat in range(0, 23):
			statName = statNames[stat]
			statLevel = separatedStats[stat].split(",")[1]
			statXP = separatedStats[stat].split(",")[2]
			statDesc += statName + ": " + statLevel + ", " + statXP + "\n"

		statEmbed.description = statDesc
		statEmbed.set_footer(icon_url=ctx.author.avatar_url,
		                     text="Requested by {} (ID: {})".format(ctx.author.display_name, ctx.author.id))
		await ctx.channel.send(embed=statEmbed)


@bot.command()
async def hcim(ctx, *, message: str):
	"""Will look up, add or remove HCIM player tracking"""

	async with aiohttp.ClientSession() as session:
		async with session.get(
				"https://secure.runescape.com/m=hiscore_oldschool_hardcore_ironman/index_lite.ws?player=" + message) as hcimLookup:
			separatedStats = (await hcimLookup.text()).split("\n")
			overallScore = int(separatedStats[0].split(",")[0])
			skillTotal = int(separatedStats[0].split(",")[1])
			scorePageNum = math.ceil(overallScore / 25)

		async with session.get(
				"https://secure.runescape.com/m=hiscore_oldschool_hardcore_ironman/overall.ws?table=0&page=" + str(
					scorePageNum)) as scorePageHTML:
			scorePageTree = html.fromstring(await scorePageHTML.text())

			playerScores = scorePageTree.xpath(
				'//tr[@class="personal-hiscores__row personal-hiscores__row--dead"]/td[2]/a/text()')
			playerScores = [name.replace('\xa0', ' ') for name in playerScores]

			if message in playerScores:
				HCIMStatusEmbed = discord.Embed(title="HCIM Status for " + message, color=0xff0000)
				HCIMStatusEmbed.description = "Player is dead! Final skill total of " + str(
					skillTotal) + " (btw)" + "\n"
				HCIMStatusEmbed.description += "[Link to Profile](https://secure.runescape.com/m=hiscore_oldschool_hardcore_ironman/hiscorepersonal.ws?user1=" + message.replace(
					" ", "%20") + ")"
				await ctx.channel.send(embed=HCIMStatusEmbed)
			else:
				HCIMStatusEmbed = discord.Embed(title="HCIM Status for " + message, color=0x00ff00)
				HCIMStatusEmbed.description = "Player is alive with a hiscore position of " + str(
					overallScore) + ", skill total of " + str(skillTotal) + " (btw)" + "\n"
				HCIMStatusEmbed.description += "[Link to Profile](https://secure.runescape.com/m=hiscore_oldschool_hardcore_ironman/hiscorepersonal.ws?user1=" + message.replace(
					" ", "%20") + ")"
				HCIMStatusEmbed.set_footer(icon_url=ctx.author.avatar_url,
				                           text="Requested by {} (ID: {})".format(ctx.author.display_name,
				                                                                  ctx.author.id))
				await ctx.channel.send(embed=HCIMStatusEmbed)


@bot.command()
async def price(ctx, *, itemName: str):
	"""Uses the RSBuddy API to fetch item prices"""

	priceAPI = "https://rsbuddy.com/exchange/summary.json"
	async with aiohttp.ClientSession() as session:
		async with session.get(priceAPI) as priceJSON:
			jsonData = json.loads(await priceJSON.text())

			closestMatchRatio = 0
			closestItemID = -1
			for item, itemData in jsonData.items():
				ratioMatch = fuzz.token_sort_ratio(itemName, itemData["name"])
				if ratioMatch > closestMatchRatio:
					closestMatchRatio = ratioMatch
					closestItemID = item

			if closestItemID != -1:
				itemPriceEmbed = discord.Embed(title="Price Lookup for " + jsonData[closestItemID]["name"],
				                               color=0xf1c40f)
				itemPriceEmbed.add_field(name="Buying Average",
				                         value="{:,} GP".format(jsonData[closestItemID]["buy_average"]),
				                         inline=True)
				itemPriceEmbed.add_field(name="Selling Average",
				                         value="{:,} GP".format(jsonData[closestItemID]["sell_average"]), inline=True)
				itemPriceEmbed.add_field(name="Overall Average",
				                         value="{:,} GP".format(jsonData[closestItemID]["overall_average"]),
				                         inline=True)

				itemPriceEmbed.add_field(name="Buying Quantity", value=jsonData[closestItemID]["buy_quantity"],
				                         inline=True)
				itemPriceEmbed.add_field(name="Selling Quantity", value=jsonData[closestItemID]["sell_quantity"],
				                         inline=True)
				itemPriceEmbed.add_field(name="Overall Quantity", value=jsonData[closestItemID]["overall_quantity"],
				                         inline=True)

				itemPriceEmbed.add_field(name="Members Item",
				                         value=str(jsonData[closestItemID]["members"]).capitalize(),
				                         inline=True)
				itemPriceEmbed.add_field(name="Item ID", value=jsonData[closestItemID]["id"], inline=True)
				itemPriceEmbed.add_field(name="Store Value", value="{:,} GP".format(jsonData[closestItemID]["sp"]),
				                         inline=True)

				itemPriceEmbed.set_footer(icon_url=ctx.author.avatar_url,
				                          text="Requested by {} (ID: {})".format(ctx.author.display_name,
				                                                                 ctx.author.id))

				await ctx.channel.send(embed=itemPriceEmbed)
			else:
				await ctx.channel.send("Item not found!")


bot.loop.create_task(anniversaryCheck())
bot.run(legionToken)
