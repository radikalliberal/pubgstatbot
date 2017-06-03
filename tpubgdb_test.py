import tinypubgdb
import matplotlib.pyplot as plt

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

#test_1()
#test_2()
#test_3()
test_4()

