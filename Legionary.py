# For Legion Discord Bot
import discord
import asyncio
import platform
from discord.ext import commands

# Other Libraries
import datetime
import os

bot = commands.Bot(command_prefix="!")

# Discord Bot Token
tokenFile = open('tokenFile', 'r')
botToken = tokenFile.readline()
tokenFile.close()

# News Channel ID
newsID = '508111231937413151'

# Talk Channel ID
talkID = '463477926961348643'

legionRoles = ['Recruit', 'Corporal', 'Sergeant', 'Lieutenant', 'Captain', 'General', 'Owner']
membersMessages = ['', '', '', '', '', '']

# Members lists
folder = "./members/"


@bot.event
async def on_ready():
    print('Logged in as ' + bot.user.name + ' (ID:' + bot.user.id + ') | Connected to ' + str(
        len(bot.servers)) + ' servers | Connected to ' + str(len(set(bot.get_all_members()))) + ' users')
    print('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__,
                                                                               platform.python_version()))


@bot.event
async def on_message(ctx):
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
    commandsEmbed.add_field(name="!recruit <@name>", value='Recruits <@name> to the clan', inline=False)
    commandsEmbed.add_field(name="!promote <@name>",
                            value='Promotes <@name> one rank higher (must already be recruited)', inline=False)

    await bot.send_message(ctx.message.channel, embed=commandsEmbed)


@bot.command(pass_context=True)
async def recruit(ctx, user: discord.Member):
    # Add their name and the current date to recruitment list
    recruitName = user.display_name
    recruitDate = datetime.datetime.today().strftime('%m/%d/%Y')

    print("[Recruiting] Recruiting " + user.display_name)

    await recruitUser(user)

    # Add their name to the recruits file
    recruitsFile = open(os.path.join(folder, "Recruit"), 'a+')
    recruitsFile.write("\n" + recruitName + "\t" + recruitDate)
    recruitsFile.close()

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
            asyncio.ensure_future(bot.replace_roles(user, newRoleID, moderatorRoleID))
        elif newRoleName == 'General':
            asyncio.ensure_future(bot.replace_roles(user, newRoleID, globalModRoleID))
        else:
            asyncio.ensure_future(bot.replace_roles(user, newRoleID))

        # Delete entry from old rank file
        oldRoleFile = open(os.path.join(folder, currentRole.name), "r")
        lines = oldRoleFile.readlines()
        oldRoleFile.close()

        oldRoleFile = open(os.path.join(folder, currentRole.name), "w")
        for line in lines:
            if user.display_name not in line:
                oldRoleFile.write(line)
        oldRoleFile.close()

        # Add entry to new file
        newRoleFile = open(os.path.join(folder, newRoleName), "a+")
        newRoleFile.write(
            "\n" + user.display_name + "\t" + datetime.datetime.today().strftime('%m/%d/%Y'))
        newRoleFile.close()

        print("[Promotion] Promoted " + user.display_name + " to " + newRoleName)

        await bot.send_message(ctx.message.channel,
                               "<@!%s> has been promoted to %s!" % (user.id, newRoleName))


@bot.command(pass_context=True)
async def members(ctx, *args):
    recruits = {}
    corporals = {}
    sergeants = {}
    lieutenants = {}
    captains = {}
    generals = {}

    for file in os.listdir(folder):
        membersFile = open(os.path.join(folder, file), 'r')
        line = membersFile.readline()

        while line:
            member = line.split()

            # If they have a multi-part name
            if (len(member) > 2):
                member[0] = " ".join(member[:-1])
                member[1] = member[-1]

            if (len(member) > 0):
                if os.path.basename(membersFile.name) == "Recruit":
                    recruits.update({member[0]: member[1]})
                if os.path.basename(membersFile.name) == "Corporal":
                    corporals.update({member[0]: member[1]})
                if os.path.basename(membersFile.name) == "Sergeant":
                    sergeants.update({member[0]: member[1]})
                if os.path.basename(membersFile.name) == "Lieutenant":
                    lieutenants.update({member[0]: member[1]})
                if os.path.basename(membersFile.name) == "Captain":
                    captains.update({member[0]: member[1]})
                if os.path.basename(membersFile.name) == "General":
                    generals.update({member[0]: member[1]})

            line = membersFile.readline()

        membersFile.close()

    recruitsEmbed = discord.Embed(title="Recruits", color=0x99aab5)
    recruitsDesc = ""
    for name, date in recruits.items():
        recruitsDesc += (name + "\t" + date + "\n")
    recruitsEmbed.description = recruitsDesc

    corporalsEmbed = discord.Embed(title="Corporals", color=0xf1c40f)
    corporalsDesc = ""
    for name, date in corporals.items():
        corporalsDesc += (name + "\t" + date + "\n")
    corporalsEmbed.description = corporalsDesc

    sergeantsEmbed = discord.Embed(title="Sergeants", color=0xe67e22)
    sergeantsDesc = ""
    for name, date in sergeants.items():
        sergeantsDesc += (name + "\t" + date + "\n")
    sergeantsEmbed.description = sergeantsDesc

    lieutenantsEmbed = discord.Embed(title="Lieutenants", color=0x9b59b6)
    lieutenantsDesc = ""
    for name, date in lieutenants.items():
        lieutenantsDesc += (name + "\t" + date + "\n")
    lieutenantsEmbed.description = lieutenantsDesc

    captainsEmbed = discord.Embed(title="Captains", color=0x992d22)
    captainsDesc = ""
    for name, date in captains.items():
        captainsDesc += (name + "\t" + date + "\n")
    captainsEmbed.description = captainsDesc

    generalsEmbed = discord.Embed(title="Generals", color=0x3498db)
    generalsDesc = ""
    for name, date in generals.items():
        generalsDesc += (name + "\t" + date + "\n")
    generalsEmbed.description = generalsDesc

    if args == "update":
        await bot.delete_message(membersMessages[0])
        await bot.delete_message(membersMessages[1])
        await bot.delete_message(membersMessages[2])
        await bot.delete_message(membersMessages[3])
        await bot.delete_message(membersMessages[4])
        await bot.delete_message(membersMessages[5])

    membersMessages[0] = await bot.send_message(ctx.message.channel, embed=recruitsEmbed)
    membersMessages[1] = await bot.send_message(ctx.message.channel, embed=corporalsEmbed)
    membersMessages[2] = await bot.send_message(ctx.message.channel, embed=sergeantsEmbed)
    membersMessages[3] = await bot.send_message(ctx.message.channel, embed=lieutenantsEmbed)
    membersMessages[4] = await bot.send_message(ctx.message.channel, embed=captainsEmbed)
    membersMessages[5] = await bot.send_message(ctx.message.channel, embed=generalsEmbed)


async def recruitUser(member):
    roleID = discord.utils.get(member.server.roles, name="Recruit")
    await bot.add_roles(member, roleID)


bot.run(botToken)
