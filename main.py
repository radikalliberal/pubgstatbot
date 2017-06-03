import discord
from discord.ext import commands
import random
import matplotlib.pyplot as plt
import matplotlib
import tinypubgdb
import numpy as np
import sys
import Pubgdataminer

bot = commands.Bot(command_prefix='?')

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
    await bot.say(name + ' has been subscribed')

@bot.command()
async def progression(names: str, *params: str):
    if len(params) < 1:
        text = '''Help: functioncall ?progression 
            ?progression **players** **match** "**stat**" [*region* *season*]

            possible parameters:
            players = one or more subscribed players, separated by colon
            region = {0}
            match = {1}                
            seasons = {2}
            "stat" <- if multiple words the quotes are needed = {3} 

            example: ?progression crazy_,DrDisRespect squad  "Longest Kill"
            '''.format(regs, matches, stat_db.getseasons(), allstats)
        await bot.say(text)
        return
    elif len(params) >= 4:
        match, stat, srv, season = params[0], params[1], params[2], params[3]
    elif len(params) == 3:
        match, stat, srv, season = params[0], params[1], params[2], stat_db.getcurrentseason()
    elif len(params) == 2:
        match, stat, srv, season = params[0], params[1], 'agg', stat_db.getcurrentseason()
    path_pic = './pics/' + names.lower() + srv.lower() + match.lower() + stat.lower() + '.png'

    print('progression '+names + ' ' + match + ' ' + stat + ' ' + srv + ' ' + season)

    with plt.rc_context({'axes.edgecolor': 'white', 'xtick.color': 'white', 'ytick.color': 'white'}):
        fig, ax = plt.subplots(nrows=1, ncols=1)
        names = names.split(',')
        x, y, x_labels = [], [], []

        for i, name in enumerate(names):
            try:
                y_, x_, x_labels_ = stat_db.progression(name, srv, match, stat, season)
                x.append(x_)
                y.append(y_)
                x_labels.append(x_labels_)
                ax.plot(x_, y_)
            except Exception as e:
                names[i] = None
                await bot.say(e)

        names = [n for n in names if n is not None]
        x = np.array(x)
        x_labels = np.array(x_labels)
        indices = [x_i for x_i in range(len(x.flatten()))]
        vals = [x.flatten(), x_labels.flatten()]
        indices.sort(key=vals[0].__getitem__)
        for i, sublist in enumerate(vals):
            vals[i] = [sublist[j] for j in indices]

        ax.grid(color=(154 / 256, 157 / 256, 162 / 256), linestyle='-', linewidth=1)
        ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator(vals[0]))
        ax.xaxis.set_major_formatter(matplotlib.ticker.FixedFormatter(vals[1]))
        ax.set_facecolor((54 / 256, 57 / 256, 62 / 256))
        fig.set_facecolor((54 / 256, 57 / 256, 62 / 256))
        title_obj = plt.title(str(names) + ': ' + srv + ', ' + match + ', ' + season, fontsize=10)
        plt.setp(title_obj, color='w')
        plt.ylabel(stat)
        plt.legend(names)
        plt.xlabel('Date')
        ax.xaxis.label.set_color('w')
        ax.yaxis.label.set_color('w')
        fig.savefig(path_pic, facecolor=fig.get_facecolor())

    await bot.upload(path_pic)

@bot.command()
async def unsubscribe(name: str):
    worked = False
    try:
        worked = stat_db.unsubscribe(name)
    except Exception as e:
        await bot.say(e)
    if worked:
        await bot.say(name + ' is unsubscribed')

@bot.command()
async def subscribers():
    await bot.say(str(stat_db.getsubscribers()))

@bot.command()
async def stats(*params: str):
    stat_db.update()
    if len(params) < 2:
        text = '''Help: functioncall ?stats 
            ?stats region match "stat" <- if multiple word the quotes are needed
            possible parameters:
            region = {0}
            match = {1}                
            stats = {2}
            
            example: ?stats agg squad "Longest Kill"
            '''.format(regs, matches, allstats)
        await bot.say(text)
        return

    elif len(params) >= 3:
        srv, match, stat = params[0], params[1], params[2]
    elif len(params) == 2:
        srv, match, stat = 'agg', params[0], params[1]


    names = stat_db.getsubscribers()
    if stat.lower() not in allstats:
        await bot.say('queryied Stat {0} not available. Choose one of these:\n{1}'.format(stat,allstats))
        return
    if srv not in regs:
        await bot.say('Server :{0} does not exist. Choose one of these.\n{1}'.format(srv,regs))
        return
    if match not in matches:
        await bot.say('matching :{0} does not exist. Choose one of these.\n{1}'.format(match,matches))


    await bot.say('working...')
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
async def update():
    stat_db.update()
    await bot.say('Database updated')


@bot.command()
async def currentseason():
    await bot.say(stat_db.getcurrentseason())

@bot.command()

async def seasons():
    stat_db.getseasons()
    await bot.say(stat_db.getseasons())

def main(argv):
    bot.run(argv[0])

if __name__ == '__main__':
    allstats = [x.lower() for x in
                ['K/D Ratio', 'Win %', 'Time Survived', 'Rounds Played', 'Wins', 'Win Top 10 Ratio', 'Top 10s',
                 'Top 10 Ratio',
                 'Losses', 'Rating', 'Best Rating', 'Damage Pg', 'Headshot Kills Pg', 'Heals Pg', 'Kills Pg',
                 'Move Distance Pg',
                 'Revives Pg', 'Road Kills Pg', 'Team Kills Pg', 'Time Survived Pg', 'Top 10s Pg', 'Kills', 'Assists',
                 'Suicides',
                 'Team Kills', 'Headshot Kills', 'Headshot Kill Ratio', 'Vehicle Destroys', 'Road Kills', 'Daily Kills',
                 'Weekly Kills', 'Round Most Kills', 'Max Kill Streaks', 'Days', 'Longest Time Survived',
                 'Most Survival Time',
                 'Avg Survival Time', 'Win Points', 'Walk Distance', 'Ride Distance', 'Move Distance',
                 'Avg Walk Distance',
                 'Avg Ride Distance', 'Longest Kill', 'Heals', 'Revives', 'Boosts', 'Damage Dealt', 'DBNOs']]

    regs = ['eu', 'na', 'as', 'sa', 'agg']
    matches = ['solo', 'duo', 'squad']

    stat_db = tinypubgdb.Tinypubgdb('db.json', Pubgdataminer.Pubgdataminer(sys.argv[2]))
    stat_db.update()
    main(sys.argv[1:])






