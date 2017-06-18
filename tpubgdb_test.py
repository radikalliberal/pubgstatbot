import tinypubgdb
import matplotlib.pyplot as plt
import ujson
import matplotlib
import Pubgdataminer
import sys

regs = ['eu', 'na', 'as', 'sa', 'agg']
matches = ['solo', 'duo', 'squad']




def test_1(stat_db):
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



def test_2(stat_db):
    stat_db.update()
    erg = stat_db.progression('crazy_', 'agg', 'squad', 'kills', '2017-pre2')
    print(erg)

def test_3(stat_db):
    stat_db.update()
    print(stat_db.getseasons())

def test_4(stat_db):
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


        def flatten(x):
            x_new = []
            for i in x:
                for k in i:
                    x_new.append(k)
            return x_new

        x = flatten(x)
        x_labels = flatten(x_labels)
        print(x)
        print(y)
        print(x_labels)
        indices = [x_i for x_i in range(len(x))]
        vals = [x, x_labels]
        print(vals)
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
        fig.savefig(path_pic, facecolor=fig.get_facecolor())

def test_6(stat_db):
    print(stat_db.stat('crazy_', 'agg', 'squad', 'speed', '2017-pre2'))

def test_7(stat_db):
    stat_db.miner.connect()
    data = ujson.loads(stat_db.miner.getdata('crazy_'))
    entry1 = stat_db.build_entry(data)
    data = ujson.loads(stat_db.miner.getdata('swordo'))
    entry2 = stat_db.build_entry(data)
    print(entry2)

def build_new_db(stat_db,new_stat_db):

    subs = stat_db.getsubscribers()
    for s in subs:
        entry = dict()
        entry['season'] = '2017-pre2'
        entry['match'] = []
        for m in stat_db.matches:
            match = dict()
            match['name'] = m
            match['stat'] = []
            for st in stat_db.allstats:
                stat = stat_db.convertstat(s, 'agg', m, st, '2017-pre2')
                stat['name'] = st
                match['stat'].append(stat)
            entry['match'].append(match)

        player_table = new_stat_db.db.table(s.lower(), cache_size=None)
        player_table.insert(entry)

import datetime


def test_new_db(stat_db):
    print(stat_db.update())
    entry = dict(stat_db.stat('crazy_', 'solo', 'k/d ratio', '2017-pre2'))
    del entry['name']
    for key in sorted(entry, reverse=True):
        print(key)
    #print(stat_db.progression2('crazy_','solo','k/d ratio','2017-pre2'))


def test_8(stat_db):
    for m in stat_db.matches:
        stat_db.lookatrankings(m, stat_db.getcurrentseason())




#test_1()
#test_2()
#test_3()
#test_4()
#test_5('crazy_,mast0r_d,swordo', 'squad', 'kills pg')


if __name__ == '__main__':
    #stat_db = tinypubgdb.Tinypubgdb('db.json', Pubgdataminer.Pubgdataminer(sys.argv[1]))
    new_stat_db = tinypubgdb.Tinypubgdb('db2.json', Pubgdataminer.Pubgdataminer(sys.argv[1]))
    #build_new_db(stat_db, new_stat_db)
    #test_new_db(new_stat_db)
    test_8(new_stat_db)