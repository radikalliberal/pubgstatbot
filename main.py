import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from discord.ext import commands
import discord
import tinypubgdb
import sys
import Pubgdataminer
import copy
import asyncio
import threading
import datetime
import numpy as np
import imageio

bot = commands.Bot(command_prefix='?')
stat_db = tinypubgdb.Tinypubgdb('db.json', Pubgdataminer.Pubgdataminer(sys.argv[2]))
updating = False


def extendlength(stri, length, mode=None):
    if mode == 'right':
        return (length - len(stri)) * ' ' + stri
    else:
        return stri + (length - len(stri)) * ' '


def table(players, match, stat, seas):

    tabl = dict()
    tab = []
    maxsize = 0
    maxsize_change = 0
    for player in players:
        try:
            entry = stat_db.stat(player, match, stat, seas)
            vals = []
            for key in sorted(entry, reverse=True):
                vals.append(entry[key])
                if len(vals) > 1:
                    vals.append(vals[0]-vals[1])
                    break

            if len(vals) < 1:
                vals = [0]
            tabl[player] = vals
        except Exception as e:
            print(e)
            tabl[player] = [0]
        print(tabl[player])
        if len(str(tabl[player][0])) > maxsize:
            maxsize = len('{:.2f}'.format(tabl[player][0]*1.0))
        if len(tabl[player]) > 1 and len('{:+.2f}'.format(tabl[player][2]*1.0)) > maxsize_change:
            maxsize_change = len('{:+.2f}'.format(tabl[player][2]*1.0))
    print(tabl)
    ordered_tabl = sorted(tabl, key=tabl.__getitem__)
    for i, x in enumerate(ordered_tabl[::-1]):
        if len(tabl[x]) > 1:
            scores = extendlength('{:.2f}'.format(tabl[x][0]*1.0), maxsize+1, 'right') + \
                     ' (' + extendlength('{:+.2f}'.format(tabl[x][2]*1.0), maxsize_change, 'right') + ')'
        else:
            scores = extendlength('{:.2f}'.format(tabl[x][0]*1.0), maxsize+1, 'right')
        tab.append(extendlength(str(i+1), 2, 'right') + '. ' + extendlength(x, 20) + scores)
    return tab


@bot.event
async def on_ready():
    #stat_db.checkuptodate()
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


async def autoupdate():
    # Todo: make daily backups of database and delete old updates older than 7 days
    await bot.wait_until_ready()
    while not bot.is_closed:
        global updating
        while updating:
            await asyncio.sleep(1)
        updating = True
        channel = discord.Object(id=327344769049034753)
        t = threading.Thread(target=stat_db.update,
                             kwargs={'forced': True})
        t.start()
        while t.is_alive():
            await asyncio.sleep(1)
        updating = False
        current_season = stat_db.getcurrentseason()
        for m in stat_db.matches:
            mset = False
            table = []
            table.append(extendlength('match', 7) + extendlength('stat', 25) +
                         extendlength('player', 20) + extendlength('score', 10))

            table.append('--------------------------------------------------------------')
            for s in stat_db.allstats:
                msg = stat_db.lookatrankings(m, s, current_season)
                await asyncio.sleep(0.1)
                if 'player' in msg:
                    if mset:
                        table.append(extendlength('', 7) + extendlength(msg['stat'], 25) +
                                     extendlength(msg['player'], 20) +
                                     extendlength('{:.2f}'.format(msg['value']), 10, 'right'))
                    else:
                        mset = True
                        table.append(extendlength(msg['match'], 7) + extendlength(msg['stat'], 25) +
                                     extendlength(msg['player'], 20) +
                                     extendlength('{:.2f}'.format(msg['value']), 10, 'right'))

            m = '**Top1 changes for Stats**\n```' + '\n'.join(table) + '```'
            print(m)
            if len(table) > 2:
                await bot.send_message(channel, m)
        await asyncio.sleep(60 * 60)


@bot.command()
async def joined(member: discord.Member):
    print('{0.name} joined in {0.joined_at}'.format(member))
    """Says when a member joined."""
    await bot.say('{0.name} joined in {0.joined_at}'.format(member))


@bot.command(description='''get stats for player
usage: ?profile <playername>
''')
async def profil(name: str):
    global updating
    if updating:
        await bot.say('updating Database please be patient.')
        while updating:
            await asyncio.sleep(1)

    await bot.type()
    stats_of_interest = ['k/d ratio',
                         'rounds played',
                         'wins',
                         'losses',
                         'kills',
                         'win %',
                         'knock outs',
                         'heals',
                         'revives',
                         'boosts',
                         'assists',
                         'suicides',
                         'rating',
                         'best rating',
                         'win top 10 ratio',
                         'top 10s',
                         'top 10 rate',
                         'headshot kill ratio',
                         'vehicle destroys',
                         'round most kills',
                         'max kill streaks',
                         'longest kill',
                         'damage dealt',
                         'damage pg',
                         'headshot kills pg',
                         'heals pg',
                         'kills pg',
                         'move distance pg',
                         'revives pg',
                         'road kills pg',
                         'team kills pg',
                         'time survived pg',
                         'top 10s pg']

    if name not in stat_db.getsubscribers():
        await bot.say('user {0} not found. rewrite Request if name was false or subscribe with "?subscribe {0}"'.format(name))
        return

    out = "**Profil: {}**\n```{}{}{}{}".format(name,
                                               extendlength('stat', 21, 'right'),
                                               extendlength('solo', 10, 'right'),
                                               extendlength('duo', 10, 'right'),
                                               extendlength('squad', 10, 'right'))
    out += '\n-----------------------------------------------------'
    await asyncio.sleep(0.2)
    for stat in stats_of_interest:
        out += '\n' + extendlength(stat, 20, 'right') + ':'
        for match in ['solo', 'duo', 'squad']:
            dic = stat_db.stat(name, match, stat, stat_db.getcurrentseason())
            if dic is None:
                value = 0
            else:
                tstamp = str(stat_db.tointtimestamp(datetime.datetime.today()))
                value = dic[tstamp]
            out += extendlength('{:.2f}'.format(value), 10, 'right')
    out += "```"
    await bot.say(out)

@bot.command(description='''plot 2 stats for x/y for every player usage: ?scatter <stat_x> <stat_y> <match>''')
async def scatter(stat_x: str, stat_y: str, match: str):
    await bot.type()
    global updating
    if updating:
        await bot.say('updating Database please be patient.')
        while updating:
            await asyncio.sleep(1)

    path_pic = ('./pics/{}_{}_{}.png'.format(stat_x, stat_y, match)).replace('/', '')
    with plt.rc_context({'axes.edgecolor': 'white', 'xtick.color': 'white', 'ytick.color': 'white', 'legend.numpoints': '1'}):
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 7))

        x, y, x_, y_ = [], [], [], []
        markers = ['o', 'p', 'D', '8']
        for i, player in enumerate(stat_db.getsubscribers()):
            steps = int(len(stat_db.getsubscribers()) ** (1/3))+1
            r = 0.2 + (0.8 * (i % steps) / steps)
            g = 0.2 + (0.8 * ((i//steps) % steps) / steps)
            b = 0.2 + (0.8 * ((i//(steps*steps)) % steps) / steps)
            xi, yi = stat_db.scatterpubg(player, stat_x, stat_y, match, stat_db.currentseason, 1)
            x.append(xi[0])
            y.append(yi[0])
            ax.scatter(xi,
                       yi,
                       alpha=1,
                       marker=markers[i//7],
                       s=120,
                       c=(r, g, b, 0.9))
        if max(x) > 0 and max(y) > 0:
            z = np.polyfit(x, y, 2)
            p = np.poly1d(z)
            x_2 = np.arange(min(x), max(x), (max(x)-min(x))/1000)
            ax.plot(x_2, p(x_2), alpha=0.4, c='#FF0040', linewidth=4)
            labels = ['polyfit'] + stat_db.getsubscribers()
        else:
            labels = stat_db.getsubscribers()

        ax.grid(color=(154 / 256, 157 / 256, 162 / 256), linestyle='-', linewidth=1)
        ax.patch.set_alpha(0.1)
        fig.patch.set_alpha(0)
        plt.ylabel(stat_y)
        plt.xlabel(stat_x)
        chartBox = ax.get_position()
        cols = len(stat_db.getsubscribers()) // 25 + 1
        ax.set_position([chartBox.x0, chartBox.y0, chartBox.width * (1-cols*0.17), chartBox.height])
        leg = ax.legend(labels,
                        loc='upper center',
                        bbox_to_anchor=(1+0.17*cols, 1),
                        prop={'size': 10},
                        ncol=cols,
                        framealpha=0.1,
                        scatterpoints=1)
        for text in leg.get_texts():
            text.set_color('w')
        ax.xaxis.label.set_color('w')
        ax.yaxis.label.set_color('w')
        fig.savefig(path_pic, facecolor=fig.get_facecolor())

        await bot.upload(path_pic)


@bot.command(description='''make a gif of 2 stats for x/y plotted for every player usage: ?scattergif <stat_x> <stat_y> <match>''')
async def scattergif(stat_x: str, stat_y: str, match: str):
    await bot.type()
    global updating

    def dnone(a):
        b = []
        for x in a:
            if x is not None:
                b.append(x)
        return b

    if updating:
        await bot.say('updating Database please be patient.')
        while updating:
            await asyncio.sleep(1)

    with plt.rc_context({'axes.edgecolor': 'white', 'xtick.color': 'white', 'ytick.color': 'white', 'legend.numpoints': '1'}):
        iterations = 20
        x, y, x_, y_, maxx, maxy = [], [], [], [], [], []
        xi, yi = {}, {}
        markers = ['o', 'p', 'D', '8']
        xi['min'], yi['min'] = 10000, 10000
        xi['max'], yi['max'] = 0, 0
        maxdata = 0
        for k, player in enumerate(stat_db.getsubscribers()):
            xii, yii = stat_db.scatterpubg(player, stat_x, stat_y, match, stat_db.currentseason, iterations)
            xi[player] = xii
            yi[player] = yii
            if len(xii) > maxdata:
                maxdata = len(xii)
            if xi['min'] > min(dnone(xii)):
                xi['min'] = min(dnone(xii))
            if yi['min'] > min(dnone(yii)):
                yi['min'] = min(dnone(yii))
            if xi['max'] < max(dnone(xii)):
                xi['max'] = max(dnone(xii))
            if yi['max'] < max(dnone(yii)):
                yi['max'] = max(dnone(yii))

        for j in range(iterations-1):
            path_pic = ('./pics/{}.png'.format(j))
            fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(7, 5))
            for i, player in enumerate(stat_db.getsubscribers()):
                steps = int(len(stat_db.getsubscribers()) ** (1/3))+1
                r = 0.2 + (0.8 * (i % steps) / steps)
                g = 0.2 + (0.8 * ((i//steps) % steps) / steps)
                b = 0.2 + (0.8 * ((i//(steps*steps)) % steps) / steps)
                #xi, yi = stat_db.scatterpubg(player, stat_x, stat_y, match, stat_db.currentseason)
                if  len(xi[player]) >= j+1 and \
                    len(yi[player]) >= j+1 and \
                        xi[player][j] is not None and yi[player][j] is not None and\
                        (xi[player][j] > 0 or yi[player][j] > 0):
                    x.append(xi[player][j])
                    y.append(yi[player][j])
                    ax.scatter(xi[player][j],
                               yi[player][j],
                               alpha=1,
                               marker=markers[i//7],
                               s=120,
                               c=(r, g, b))
                else:
                    ax.scatter(0,
                               0,
                               alpha=0,
                               marker=markers[i // 7],
                               s=120,
                               c=(r, g, b))
            if len(x) > 0 and len(y) > 0 and max(x) > 0 and max(y) > 0:
                z = np.polyfit(x, y, 2)
                p = np.poly1d(z)
                x_2 = np.arange(xi['min'], xi['max'], (xi['max'] - xi['min'])/1000)
                ax.plot(x_2, p(x_2), alpha=0.4, c='#FF0040', linewidth=4)
                labels = ['polyfit'] + stat_db.getsubscribers()
            else:
                labels = stat_db.getsubscribers()

            title_obj = plt.title((datetime.datetime.today() - datetime.timedelta(days=iterations-j-1)).date(),
                                  fontsize=20)
            plt.setp(title_obj, color='w')
            ax.grid(color=(1, 1, 1), linestyle='--', linewidth=1)
            ax.patch.set_color((54/256, 57/256, 62/256))
            fig.patch.set_color((54/256, 57/256, 62/256))
            plt.ylabel(stat_y)
            plt.xlabel(stat_x)
            chartBox = ax.get_position()
            cols = len(stat_db.getsubscribers()) // 25 + 1
            ax.set_position([chartBox.x0, chartBox.y0, chartBox.width * (1-cols*0.17), chartBox.height])
            plt.ylim((yi['min']*0.9, yi['max']*1.1))
            plt.xlim((xi['min']*0.9, xi['max']*1.1))
            leg = ax.legend(labels,
                            loc='upper center',
                            bbox_to_anchor=(1+0.17*cols, 1),
                            prop={'size': 7},
                            ncol=cols,
                            framealpha=0.1,
                            scatterpoints=1)
            for text in leg.get_texts():
                text.set_color('w')
            ax.xaxis.label.set_color('w')
            ax.yaxis.label.set_color('w')
            fig.savefig(path_pic, facecolor=fig.get_facecolor())
            plt.close(fig)

        filenames_blend = []
        filenames = ['./pics/{}.png'.format(x) for x in range(iterations - 1)]
        #for i,fn in enumerate(filenames):
        #    if i == len(filenames)-1:
        #        break
        #    im1 = imageio.imread(filenames[i])
        #    im2 = imageio.imread(filenames[i+1])
        #    imageio.imwrite('./pics/{}.png'.format(i), im1/2+im1/2)
        #    filenames_blend.append(fn)
        #    for k in range(4):
        #        imageio.imwrite('./pics/{}blend{}.png'.format(i, k), im2/(1-0.2*(k+1))+im1/(0.2*(k+1)))
        #        filenames_blend.append('./pics/{}blend{}.png'.format(i, k))

        images = []
        #print(filenames_blend)
        for filename in filenames:
            images.append(imageio.imread(filename))
        imageio.mimsave('./pics/scatter.gif', images, fps=6, loop=1)
        await bot.upload('./pics/scatter.gif')


@bot.command(description='use to subscribe a player to the database to track stats')
async def subscribe(name: str):
    global updating
    if updating:
        await bot.say('updating Database please be patient.')
        while updating:
            await asyncio.sleep(1)

    await bot.type()
    print('?subscribe ' + name)
    try:
        stat_db.subscribe(name)
        stat_db.checkuptodate()
        for player in stat_db.getsubscribers():
            stat_db.update(player)
            await asyncio.sleep(0.1)
        await bot.say(name + ' has been subscribed')
    except Exception as e:
        await bot.say(e)


@bot.command(description='''draw graph of player performance over time for a specific stat

            ?progression players "stat" [match [season]]
            possible parameters:
            players = one or more subscribed players, separated by colon
            match = {0}                
            seasons = {1}
            "stat" <- if multiple words the quotes are needed = {2} 

            example: ?progression crazy_,DrDisRespect squad  "Longest Kill"
            '''.format(stat_db.matches, stat_db.getseasons(), stat_db.allstats))
async def progression(*params: str):
    global updating
    if updating:
        await bot.say('updating Database please be patient.')
        while updating:
            await asyncio.sleep(1)

    if len(params) < 2:
        text = '''```Help: function call ?progression 
            ?progression players "stat" [match [season]]

            possible parameters:
            players = one or more subscribed players, separated by colon
            match = {0}                
            seasons = {1}
            "stat" <- if multiple words the quotes are needed = {2} 

            example: ?progression crazy_,DrDisRespect squad  "Longest Kill"
            ```'''.format(stat_db.matches, stat_db.getseasons(), stat_db.allstats)
        await bot.say(text)
        return
    elif len(params) >= 5:
        match, srv, season = [params[2]], params[3], params[4]
    elif len(params) == 4:
        match, srv, season = [params[2]], params[3], stat_db.currentseason
    elif len(params) == 3:
        match, srv, season = [params[2]], 'agg', stat_db.currentseason
    elif len(params) == 2:
        match, srv, season = ['solo', 'duo', 'squad'], 'agg', stat_db.currentseason

    names, stat = params[0], params[1]
    stat_db.checkuptodate()

    print('?progression '+names + ' ' + str(match) + ' ' + stat + ' ' + srv + ' ' + season)
    names = names.split(',')

    for m in match:
        names_for_match = copy.deepcopy(names)
        await bot.type()
        path_pic = './pics/' + (str(names_for_match).lower() + srv.lower() + str(m).lower() + stat.lower() + '.png').replace('/', '')
        with plt.rc_context({'axes.edgecolor': 'white', 'xtick.color': 'white', 'ytick.color': 'white', 'image.cmap': 'tab20'}):
            fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(14, 8))

            x, y, x_labels = [], [], []
            markers = ['o', 'p', 'D', '8']
            for i, name in enumerate(names_for_match):
                try:
                    y_, x_, x_labels_ = stat_db.progression(name, m, stat, season)
                    indices = [x_i for x_i in range(len(x_))]
                    sorted = [y_, x_, x_labels_]
                    indices.sort(key=sorted[1].__getitem__)
                    for i, sublist in enumerate(sorted):
                        sorted[i] = [sublist[j] for j in indices]

                    if 0 not in sorted[1] and not len(sorted) < 1:
                        # Todo: That can be done better
                        x.append(sorted[1])
                        y.append(sorted[0])
                        x_labels.append(sorted[2])
                        ax.plot(sorted[1], sorted[0], linewidth=2, marker=markers[i//7],  markersize=8)

                except Exception as e:
                    names_for_match[i] = None
                    await bot.say('No Data for {}/{}/{}/{}/{} Error: {}'.format(name, srv, m, stat, season, str(e)))

            names_for_match = [n for n in names_for_match if n is not None]

            def flattenunique(x):
                x_new = []
                for i in x:
                    for k in i:
                        if k in x_new:
                            continue
                        x_new.append(k)
                return x_new

            x = flattenunique(x)
            x_labels = flattenunique(x_labels)
            indices = [x_i for x_i in range(len(x))]
            vals = [x, x_labels]
            indices.sort(key=vals[0].__getitem__)
            for i, sublist in enumerate(vals):
                vals[i] = [sublist[j] for j in indices]

            spaces = len(vals[1]) // 5
            for i in range(len(vals[1])):
                if i % spaces != 0:
                    vals[1][i] = ''

            ax.grid(color=(154 / 256, 157 / 256, 162 / 256), linestyle='-', linewidth=1)
            ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator(vals[0]))
            ax.xaxis.set_major_formatter(matplotlib.ticker.FixedFormatter(vals[1]))
            ax.patch.set_alpha(0.1)
            fig.patch.set_alpha(0)
            title_obj = plt.title(str(names_for_match) + ': ' + srv + ', ' + m + ', ' + season, fontsize=10)
            plt.setp(title_obj, color='w')
            plt.ylabel(stat)
            chartBox = ax.get_position()
            ax.set_position([chartBox.x0, chartBox.y0, chartBox.width * 0.7, chartBox.height])
            leg = ax.legend(names_for_match, loc='upper center', bbox_to_anchor=(1.2, 1), ncol=1,
                            framealpha=0.1)
            for text in leg.get_texts():
                text.set_color('w')
            plt.xlabel('Date')
            ax.xaxis.label.set_color('w')
            ax.yaxis.label.set_color('w')
            fig.savefig(path_pic, facecolor=fig.get_facecolor())

        await bot.upload(path_pic)


@bot.command(description='stop tracking a subscribed player, existing data will not be deleted')
async def unsubscribe(name: str):
    global updating
    if updating:
        await bot.say('updating Database please be patient.')
        while updating:
            await asyncio.sleep(1)
    await bot.type()
    print('?unsubscribe ' + name)
    worked = False
    try:
        worked = stat_db.unsubscribe(name)
    except Exception as e:
        await bot.say(e)
    if worked:
        await bot.say(name + ' is unsubscribed')


@bot.command(description='list all subscribed Players')
async def subscribers():
    global updating
    if updating:
        await bot.say('updating Database please be patient.')
        while updating:
            await asyncio.sleep(1)
    await bot.type()
    print('?subscribers')
    await bot.say(str(stat_db.getsubscribers()))

# Todo: nur die aktuelle Saison zeigen und noch einen Parameter für saeson einfügen
@bot.command(description='''show ranking of all subscribed players for a specific stat

            ?stats "stat" [match [season]]   
            possible parameters:
            match = {0}                
            season = {1}
            stats <- if multiple words the quotes are needed = {2}
            
            example: ?stats "Longest Kill" squad eu
            ```'''.format(stat_db.matches, stat_db.getseasons(), stat_db.allstats))
async def stats(*params: str):
    global updating
    if updating:
        await bot.say('updating Database please be patient.')
        while updating:
            await asyncio.sleep(1)

    if len(params) < 1:
        text = '''```Help: functioncall ?stats 
            ?stats "stat" [match [season]]   
            possible parameters:
            match = {0}                
            season = {1}
            stats <- if multiple words the quotes are needed = {2}
            
            example: ?stats "Longest Kill" squad 2017-pre2
            ```'''.format(stat_db.matches, stat_db.getseasons(), stat_db.allstats)
        await bot.say(text)
        return

    elif len(params) >= 3:
        stat, match, season = params[0], [params[1]], params[2]
    elif len(params) == 2:
        stat, match, season = params[0], [params[1]], stat_db.currentseason
    elif len(params) == 1:
        stat, match, season = params[0], ['solo', 'duo', 'squad'], stat_db.currentseason

    match2 = ''
    for m in match:
        match2 = match2 + ',' + m

    print('?stats ' + season + ' ' + match2 + ' ' + stat)
    stat_db.checkuptodate()
    names = stat_db.getsubscribers()
    if stat.lower() not in stat_db.allstats:
        await bot.say('```queryied Stat {0} not available.\n\nChoose one of these:\n{1}```'.format(stat, stat_db.allstats))
        return
    if season not in stat_db.getseasons():
        await bot.say('```Server :{0} does not exist.\n\nChoose one of these.\n{1}```'.format(season, stat_db.getseasons()))
        return
    if match[0] not in stat_db.matches:
        await bot.say('```matching :{0} does not exist.\n\nChoose one of these.\n{1}```'.format(match, stat_db.matches))

    for m in match:
        await bot.type()
        out = "```\n" + season + '\n------------------------------------------\n'
        t = table(names, m, stat, season)
        for entry in t:
                out = out + entry + '\n'
        out = out + '\n'

        await bot.say('Ranking - ' + m + ' - ' + stat + '\n' + out + '```')


#@bot.command(description='update the database, use "?update force" to overwrite the last update with newer numbers for the day')
#async def update(*forced: str):
#    global updating
#    if updating:
#        await bot.say('already updating Database please be patient.')
#        return
#
#    await bot.type()
#    stat_db.checkuptodate()
#    print('?update {}'.format(forced))
#    if len(forced) == 1:
#        if forced[0] == 'force':
#            updating = True
#            for player in stat_db.getsubscribers():
#                stat_db.update(player, forced=True)
#                await asyncio.sleep(0.1)
#            updating = False
#            await bot.say('Database update forced')
#        else:
#            await bot.say('use either "?update" or "?update force"\
#                                    \n force does overwrite the last capture from today with new data if available')
#    elif len(forced) > 1:
#        await bot.say('use either "?update" or "?update force"\
#                        \n force does overwrite the last capture from today with new data if available')
#    else:
#        for player in stat_db.getsubscribers():
#            stat_db.update(player)
#            await asyncio.sleep(0.1)
#        await bot.say('Database updated')


@bot.command(description='returns the current season for pubg')
async def currentseason():
    global updating
    if updating:
        await bot.say('updating Database please be patient.')
        while updating:
            await asyncio.sleep(1)
    await bot.type()
    print('?currentseason')
    await bot.say(stat_db.currentseason)


@bot.command(description='returns all seasons tracked in the database')
async def seasons():
    global updating
    if updating:
        await bot.say('updating Database please be patient.')
        while updating:
            await asyncio.sleep(1)
    print('?seasons')
    await bot.type()
    stat_db.getseasons()
    await bot.say(stat_db.getseasons())


if __name__ == '__main__':
    for i, x in enumerate(sys.argv):
        print('argv['+str(i)+']:'+x)
    if len(sys.argv) == 3:
        bot.loop.create_task(autoupdate())
    if len(sys.argv) > 3:
        if sys.argv[3] == '-noautoupdate':
            pass
        else:
            pass
            bot.loop.create_task(autoupdate())
    bot.run(sys.argv[1])







