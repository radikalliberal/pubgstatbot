import discord
from discord.ext import commands
import random
import http.client
from pubgstats import *

allstats = [x.lower() for x in ['K/D Ratio','Win %','Time Survived','Rounds Played','Wins','Win Top 10 Ratio','Top 10s','Top 10 Ratio',
         'Losses','Rating','Best Rating','Damage Pg','Headshot Kills Pg','Heals Pg','Kills Pg','Move Distance Pg',
         'Revives Pg','Road Kills Pg','Team Kills Pg','Time Survived Pg','Top 10s Pg','Kills','Assists','Suicides',
         'Team Kills','Headshot Kills','Headshot Kill Ratio','Vehicle Destroys','Road Kills','Daily Kills',
         'Weekly Kills','Round Most Kills','Max Kill Streaks','Days','Longest Time Survived','Most Survival Time',
         'Avg Survival Time','Win Points','Walk Distance','Ride Distance','Move Distance','Avg Walk Distance',
         'Avg Ride Distance','Longest Kill','Heals','Revives','Boosts','Damage Dealt','DBNOs']]


regs = ['eu','na','as','sa','agg']

matches = ['solo','duo','squad']

description = '''An example bot to showcase the discord.ext.commands extension
module.
There are a number of utility commands being showcased here.'''
bot = commands.Bot(command_prefix='?', description=description)
client = discord.Client()

def table(players,srv,match,stat,seas):
    table = dict()
    tab = []
    for player in players:
        table[player.getname()] = player.stat(srv, match, stat,seas)
    ordered_table = sorted(table, key=table.__getitem__)
    for i, x in enumerate(ordered_table[::-1]):
        tab.append(str(i+1) + '. ' + x + ' - ' + str(table[x]))
    return tab

def getseasons(players):
    seas = []
    for p in players:
        seas = seas + p.agg.seasons
    return sorted(set(seas))

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def add(left : int, right : int):
    """Adds two numbers together."""
    await bot.say(left + right)

@bot.command()
async def subscribe(name: str):
    conn = http.client.HTTPSConnection("pubgtracker.com", port=443)
    conn.connect()
    conn.request("GET", '/api/profile/pc/' + name, headers={'TRN-Api-Key': '9c4b760c-b8bf-481f-a720-7a5d1c87870c'})
    response = conn.getresponse()
    res = response.read().decode("utf-8")
    data = json.loads(res)
    conn.close()
    if data['AccountId'] is None:
        await bot.say(name + ' existiert nicht')
        return

    f = open('subs.txt', 'a')
    f.write(name + '\n')
    f.close()
    await bot.say(name + ' wurde in die Subscriberliste aufgenommen')


@bot.command()
async def unsubscribe(name: str):
    found = False
    names = ''
    with open('subs.txt') as f:
        for line in f:
            if line.lower().replace('\n','') == name.lower():
                found = True
            else:
                names = names + line

    if found:
        await bot.say(name + ' wurde aus der Subscriberliste gelöscht')
        f = open('subs.txt', 'w')
        f.write(names)
        f.close()
    else:
        await bot.say(name + ' ist nicht in der Subscriberliste vorhanden')




@bot.command()
async def subscribers():
    response = ''
    with open('subs.txt') as f:
        names = [line.replace('\n','') for line in iter(f.readline, '')]
    for entry in names:
        response = response + entry + '\n'
    await bot.say(response)

@bot.command()
async def stats(*params: str):
    if len(params) < 2:
        text = '''Hilfe: Funktionsaufruf ?stats 
            Aufruf:   ?stats region match "stat" <- Achtung Anführungszeichen u.U. notwendig
            Mögliche Parameter:
            region = {0}
            match = {1}                
            stats = {2}
            
            Beispiel: ?stats agg squad "Longest Kill"
            '''.format(regs, matches, allstats)
        await bot.say(text)
        return

    elif len(params) >= 3:
        srv, match, stat = params[0], params[1], params[2]
    elif len(params) == 2:
        srv, match, stat = 'agg', params[0], params[1]

    with open('subs.txt') as f:
        names = [line.replace('\n','')
                 for line in iter(f.readline, '')]

    print(names)
    if stat.lower() not in allstats:
        await bot.say('geforderter Stat {0} nicht enthalten. Wähle aus diesen hier aus:\n{1}'.format(stat,allstats))
        return
    if srv not in regs:
        await bot.say('Der Server:{0} existiert nicht. Wähle aus diesen Optionen aus.\n{1}'.format(srv,regs))
        return
    if match not in matches:
        await bot.say('Das Match:{0} existiert nicht. Wähle aus diesen Optionen aus.\n{1}'.format(match,matches))


    await bot.say('Anfrage wird bearbeitet...')
    players = []
    conn = http.client.HTTPSConnection("pubgtracker.com", port=443)
    conn.connect()
    for name in names:
        conn.request("GET", '/api/profile/pc/' + name, headers={'TRN-Api-Key': '9c4b760c-b8bf-481f-a720-7a5d1c87870c'})
        response = conn.getresponse()
        res = response.read().decode("utf-8")
        print(res)
        data = json.loads(res)


        players.append(Pubgstats(data))

    conn.close()
    seasons = getseasons(players)
    out = ''
    #try:
    for s in seasons:
        out = out + s + '\n----------------\n'
        t = table(players,srv,match,stat,s)
        for entry in t:
            out = out + entry + '\n'
        out = out + '\n'
    #except Exception as e:
    #    print(e)
    #    await bot.say('Fehler ...')

    await bot.say('Ranking - ' + match + ' - ' + stat + '\n' + out)




@bot.command()
async def roll(dice : str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await bot.say('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await bot.say(result)

@bot.command(description='For when you wanna settle the score some other way')
async def choose(*choices : str):
    """Chooses between multiple choices."""
    await bot.say(random.choice(choices))

@bot.command()
async def repeat(times : int, content='repeating...'):
    """Repeats a message multiple times."""
    for i in range(times):
        await bot.say(content)

@bot.command()
async def joined(member : discord.Member):
    """Says when a member joined."""
    await bot.say('{0.name} joined in {0.joined_at}'.format(member))

@bot.group(pass_context=True)
async def cool(ctx):
    """Says if a user is cool.
    In reality this just checks if a subcommand is being invoked.
    """
    if ctx.invoked_subcommand is None:
        await bot.say('No, {0.subcommand_passed} is not cool'.format(ctx))

@cool.command(name='bot')
async def _bot():
    """Is the bot cool?"""
    await bot.say('Yes, the bot is cool.')




bot.run('MzE5NTkwODk3MTc4Mzc4MjQw.DBDP0Q._4jfpQcfOIx91sTuUiquyDbSK3Y')

