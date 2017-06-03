import tinypubgdb
import matplotlib.pyplot as plt
import numpy as np
import matplotlib

regs = ['eu', 'na', 'as', 'sa', 'agg']
matches = ['solo', 'duo', 'squad']
stat_db = tinypubgdb.Tinypubgdb('db.json')


def test_1():
    try:
        stat_db.unsubscribe('DrDisRespect')
    except Exception as e:
        print(e)
    try:
        stat_db.subscribe('crazy_')
        stat_db.subscribe('DrDisRespect')
    except Exception as e:
        print(e)
    try:
        stat_db.subscribe('DrDisRespect')
    except Exception as e:
        print(e)



def test_2():
    stat_db.update()
    erg = stat_db.progression('crazy_', 'agg', 'squad', 'kills', '2017-pre2')
    print(erg)

def test_3():
    stat_db.update()
    print(stat_db.getseasons())

def test_4():
    x = [1,2]
    y = [1,2]
    x_labels = ['123','234']
    with plt.rc_context({'axes.edgecolor': 'white', 'xtick.color': 'white', 'ytick.color': 'white'}):
        fig, ax = plt.subplots(nrows=1, ncols=1)
        p = ax.plot(y, x)
        ax.set_xticklabels(x_labels)
        ax.set_facecolor((54 / 256, 57 / 256, 62 / 256))
        fig.set_facecolor((54 / 256, 57 / 256, 62 / 256))
        fig.savefig('tmp.png',facecolor=fig.get_facecolor())
    print(x)
    print(y)

def test_5(names: str, *params: str):
    if len(params) < 1:
        text = '''Hilfe: Funktionsaufruf ?progression 
            Aufruf:   ?mprogression **players** **match** "**stat**" [*region* *season*]

            Mögliche Parameter:
            players = 1 oder mehr Spieler, die subscribed sind (kommaseperiert)
            region = {0}
            match = {1}                
            seasons = {2}
            stats <- Achtung Anführungszeichen u.U. notwendig = {3} 

            Beispiel: ?progression crazy_,DrDisRespect squad  "Longest Kill"
            '''.format(regs, matches, stat_db.getseasons(), '')

        return
    elif len(params) >= 4:
        match, stat, srv, season = params[0], params[1], params[2], params[3]
    elif len(params) == 3:
        match, stat, srv, season = params[0], params[1], params[2], stat_db.getcurrentseason()
    elif len(params) == 2:
        match, stat, srv, season = params[0], params[1], 'agg', stat_db.getcurrentseason()

    print(match)
    print(stat)
    print(srv)
    print(season)

    path_pic = './pics/' + names.lower() + srv.lower() + match.lower() + stat.lower() + '.png'


    with plt.rc_context({'axes.edgecolor': 'white', 'xtick.color': 'white', 'ytick.color': 'white'}):
        fig, ax = plt.subplots(nrows=1, ncols=1)
        names = names.split(',')
        x, y, x_labels = [], [], []

        for i, name in enumerate(names):
            y_, x_, x_labels_ = stat_db.progression(name, srv, match, stat, season)
            x.append(x_)
            y.append(y_)
            x_labels.append(x_labels_)
            ax.plot(x_, y_)

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
        plt.xlabel('Datum')
        ax.xaxis.label.set_color('w')
        ax.yaxis.label.set_color('w')
        plt.savefig(path_pic, facecolor=fig.get_facecolor())

#test_1()
#test_2()
#test_3()
test_4()
test_5('crazy_,DrDisRespect,swordo', 'squad', 'kills')

