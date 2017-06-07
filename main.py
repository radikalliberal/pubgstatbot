from discord.ext import commands
import matplotlib.pyplot as plt
import matplotlib
import tinypubgdb
import sys
import Pubgdataminer
import random
import copy

bot = commands.Bot(command_prefix='?')


def table(players, srv, match, stat, seas):

    def extendlength(stri, length, mode=None):
        if mode == 'right':
            return (length - len(stri)) * ' ' + stri
        else:
            return stri + (length-len(stri)) * ' '


    table = dict()
    tab = []
    maxsize = 0
    maxsize_change = 0
    for player in players:
        try:
            table[player] = stat_db.stat(player, srv, match, stat, seas)
        except Exception as e:
            print(e)
            table[player] = [0]

        if len(str(table[player][0])) > maxsize:
            maxsize = len('{:.2f}'.format(table[player][0]*1.0))
        if len(table[player]) > 1 and len('{:+.2f}'.format(table[player][2]*1.0)) > maxsize_change:
            maxsize_change = len('{:+.2f}'.format(table[player][2]*1.0))
    print(table)
    ordered_table = sorted(table, key=table.__getitem__)
    for i, x in enumerate(ordered_table[::-1]):
        if len(table[x]) > 1:
            scores = extendlength('{:.2f}'.format(table[x][0]*1.0), maxsize+1, 'right') + ' (' + extendlength('{:+.2f}'.format(table[x][2]*1.0), maxsize_change, 'right') + ')'
        else:
            scores = extendlength('{:.2f}'.format(table[x][0]*1.0), maxsize+1, 'right')
        tab.append(extendlength(str(i+1), 2) + '. ' + extendlength(x, 20) + scores)
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
    print('?subscribe ' + name)
    try:
        stat_db.subscribe(name)
    except Exception as e:
        await bot.say(e)
    await bot.say(name + ' has been subscribed')


@bot.command()
async def progression(*params: str):
    if len(params) < 2:
        text = '''```Help: function call ?progression 
            ?progression players "stat" [match [region [season]]]

            possible parameters:
            players = one or more subscribed players, separated by colon
            region = {0}
            match = {1}                
            seasons = {2}
            "stat" <- if multiple words the quotes are needed = {3} 

            example: ?progression crazy_,DrDisRespect squad  "Longest Kill"
            ```'''.format(stat_db.regs, stat_db.matches, stat_db.getseasons(), stat_db.allstats)
        await bot.say(text)
        return
    elif len(params) >= 5:
        match, srv, season = [params[2]], params[3], params[4]
    elif len(params) == 4:
        match, srv, season = [params[2]], params[3], stat_db.getcurrentseason()
    elif len(params) == 3:
        match, srv, season = [params[2]], 'agg', stat_db.getcurrentseason()
    elif len(params) == 2:
        match, srv, season = ['solo', 'duo', 'squad'], 'agg', stat_db.getcurrentseason()

    names, stat = params[0], params[1]

    if stat.lower() == 'penis':
        bot.say("No progress for penis, still short ...")
        return



    print('?progression '+names + ' ' + str(match) + ' ' + stat + ' ' + srv + ' ' + season)
    names = names.split(',')

    for m in match:
        names_for_match = copy.deepcopy(names)

        path_pic = './pics/' + str(names_for_match).lower() + srv.lower() + str(m).lower() + stat.lower() + '.png'
        #path_pic = './pics/tmp.png'
        with plt.rc_context({'axes.edgecolor': 'white', 'xtick.color': 'white', 'ytick.color': 'white'}):
            fig, ax = plt.subplots(nrows=1, ncols=1)

            x, y, x_labels = [], [], []

            for i, name in enumerate(names_for_match):
                try:
                    y_, x_, x_labels_ = stat_db.progression(name, srv, m, stat, season)

                    if 0 not in x_ and len(x_) > 1:
                        # Todo: That can be done better
                        x.append(x_)
                        y.append(y_)
                        x_labels.append(x_labels_)
                        ax.plot(x_, y_)
                    else:
                        names_for_match[i] = None
                except Exception as e:
                    names_for_match[i] = None
                    await bot.say('No Data for {}/{}/{}/{}/{} Error: {}'.format(name, srv, m, stat, season, str(e)))

            names_for_match = [n for n in names_for_match if n is not None]

            def flatten(x):
                x_new = []
                for i in x:
                    for k in i:
                        x_new.append(k)
                return x_new

            x = flatten(x)
            x_labels = flatten(x_labels)
            indices = [x_i for x_i in range(len(x))]
            vals = [x, x_labels]
            indices.sort(key=vals[0].__getitem__)
            for i, sublist in enumerate(vals):
                vals[i] = [sublist[j] for j in indices]

            print(vals)

            ax.grid(color=(154 / 256, 157 / 256, 162 / 256), linestyle='-', linewidth=1)
            ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator(vals[0]))
            ax.xaxis.set_major_formatter(matplotlib.ticker.FixedFormatter(vals[1]))
            ax.set_facecolor((54 / 256, 57 / 256, 62 / 256))
            fig.set_facecolor((54 / 256, 57 / 256, 62 / 256))
            title_obj = plt.title(str(names_for_match) + ': ' + srv + ', ' + m + ', ' + season, fontsize=10)
            plt.setp(title_obj, color='w')
            plt.ylabel(stat)
            plt.legend(names_for_match)
            plt.xlabel('Date')
            ax.xaxis.label.set_color('w')
            ax.yaxis.label.set_color('w')
            fig.savefig(path_pic, facecolor=fig.get_facecolor())

        await bot.upload(path_pic)


@bot.command()
async def unsubscribe(name: str):
    print('?unsubscribe ' + name)
    worked = False
    try:
        worked = stat_db.unsubscribe(name)
    except Exception as e:
        await bot.say(e)
    if worked:
        await bot.say(name + ' is unsubscribed')


@bot.command()
async def subscribers():
    print('?subscribers')
    await bot.say(str(stat_db.getsubscribers()))


@bot.command()
async def stats(*params: str):
    if len(params) < 1:
        text = '''```Help: functioncall ?stats 
            ?stats "stat" match region   
            possible parameters:
            region = {0}
            match = {1}                
            stats <- if multiple words the quotes are needed = {2}
            
            example: ?stats agg squad "Longest Kill"
            ```'''.format(stat_db.regs, stat_db.matches, stat_db.allstats)
        await bot.say(text)
        return

    elif len(params) >= 3:
        stat, match, srv = params[0], [params[1]], params[2]
    elif len(params) == 2:
        stat, match, srv = params[0], [params[1]], 'agg'
    elif len(params) == 1:
        stat, match, srv = params[0], ['solo', 'duo', 'squad'], 'agg'

    match2 = ''
    for m in match:
        match2 = match2 + ',' + m

    print('?stats ' + srv + ' ' + match2 + ' ' + stat)

    names = stat_db.getsubscribers()
    if stat.lower() not in stat_db.allstats:
        await bot.say('queryied Stat {0} not available. Choose one of these:\n{1}'.format(stat, stat_db.allstats))
        return
    if srv not in stat_db.regs:
        await bot.say('Server :{0} does not exist. Choose one of these.\n{1}'.format(srv, stat_db.regs))
        return
    if match[0] not in stat_db.matches:
        await bot.say('matching :{0} does not exist. Choose one of these.\n{1}'.format(match, stat_db.matches))

    await bot.say('working...')
    for m in match:
        seasons = stat_db.getseasons()
        out = "```\n"
        for s in seasons:

                out = out + s + '\n------------------------------------------\n'
                t = table(names, srv, m, stat, s)
                for entry in t:
                        out = out + entry + '\n'
                out = out + '\n'

        await bot.say('Ranking - ' + m + ' - ' + stat + '\n' + out + '```')


@bot.command()
async def update(*forced: str):
    await bot.say('working...')
    print('?update {}'.format(forced))
    if forced[0] == 'force':
        stat_db.update(forced=True)
        await bot.say('Database update forced')
    elif len(forced) > 1:
        await bot.say('use either "?update" or "?update force"\
                        \n force does overwrite the last capture from today with new data if available')
    else:
        stat_db.update()
        await bot.say('Database updated')


@bot.command()
async def currentseason():
    print('?currentseason')
    await bot.say(stat_db.getcurrentseason())


@bot.command()
async def seasons():
    print('?seasons')
    stat_db.getseasons()
    await bot.say(stat_db.getseasons())

if __name__ == '__main__':

    stat_db = tinypubgdb.Tinypubgdb('db.json', Pubgdataminer.Pubgdataminer(sys.argv[2]))
    stat_db.update()
    bot.run(sys.argv[1])







