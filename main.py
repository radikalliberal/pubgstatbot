import discord
from discord.ext import commands
import random
import matplotlib.pyplot as plt
import matplotlib
import tinypubgdb

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
stat_db = tinypubgdb.Tinypubgdb('db.json')
stat_db.update()

def table(players,srv,match,stat,seas):

    def extendlength(str, length):
        return str + (length-len(str)) * ' '

    table = dict()
    tab = []
    for player in players:
        table[player] = stat_db.stat(player, srv, match, stat,seas)
    ordered_table = sorted(table, key=table.__getitem__)
    for i, x in enumerate(ordered_table[::-1]):
        tab.append(extendlength(str(i+1),2) + '. ' + extendlength(x,20) + extendlength(str(table[x]),10))
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
async def subscribe(name: str):
    try:
        stat_db.subscribe(name)
    except Exception as e:
        await bot.say(e)
    await bot.say(name + ' wurde in die Subscriberliste aufgenommen')

@bot.command()
async  def progression(name: str, *params: str):
    if len(params) < 1:
        text = '''Hilfe: Funktionsaufruf ?progression 
            Aufruf:   ?progression player region match season "stat" <- Achtung Anführungszeichen u.U. notwendig
            Mögliche Parameter:
            region = {0}
            match = {1}                
            stats = {2}

            Beispiel: ?stats agg squad "Longest Kill"
            '''.format(regs, matches, allstats)
        await bot.say(text)
        return

    elif len(params) >= 4:
        srv, match, stat, season = params[0], params[1], params[3], params[2]
    elif len(params) == 3:
        srv, match, stat, season = params[0], params[1], params[2], max(stat_db.getseasons())
    elif len(params) == 2:
        srv, match, stat = 'agg', params[0], params[1]
    x, y, x_labels = stat_db.progression(name, srv, match, stat, params[2])
    with plt.rc_context({'axes.edgecolor': 'white', 'xtick.color': 'white', 'ytick.color': 'white'}):
        fig, ax = plt.subplots(nrows=1, ncols=1)
        p = ax.plot(y, x)
        ax.set_xticklabels(x_labels)
        ax.set_facecolor((54 / 256, 57 / 256, 62 / 256))
        fig.set_facecolor((54 / 256, 57 / 256, 62 / 256))
        title_obj = plt.title(name + ': ' + srv + ', '+ match + ', '+ season  , fontsize=20)
        plt.setp(title_obj, color='w')
        plt.ylabel(stat)
        plt.xlabel('Datum')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')

        fig.savefig('tmp.png',facecolor=fig.get_facecolor())
    print(x)
    print(y)

    #
    await bot.upload('tmp.png')


@bot.command()
async def unsubscribe(name: str):
    worked = False
    try:
        worked = stat_db.unsubscribe(name)
    except Exception as e:
        await bot.say(e)
    if worked:
        await bot.say(name + ' wurde unsubscribed')

@bot.command()
async def subscribers():
    await bot.say(str(stat_db.getsubscribers()))

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


    names = stat_db.getsubscribers()
    if stat.lower() not in allstats:
        await bot.say('geforderter Stat {0} nicht enthalten. Wähle aus diesen hier aus:\n{1}'.format(stat,allstats))
        return
    if srv not in regs:
        await bot.say('Der Server:{0} existiert nicht. Wähle aus diesen Optionen aus.\n{1}'.format(srv,regs))
        return
    if match not in matches:
        await bot.say('Das Match:{0} existiert nicht. Wähle aus diesen Optionen aus.\n{1}'.format(match,matches))


    await bot.say('Anfrage wird bearbeitet...')
    seasons = stat_db.getseasons()
    out = "```\n"
    for s in seasons:
        out = out + s + '\n-------------------------\n'
        t = table(names,srv,match,stat,s)
        for entry in t:
            out = out + entry + '\n'
        out = out + '\n'

    await bot.say('Ranking - ' + match + ' - ' + stat + '\n' + out + '```')

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

bot.run('MzE5NTkwODk3MTc4Mzc4MjQw.DBDP0Q._4jfpQcfOIx91sTuUiquyDbSK3Y')




