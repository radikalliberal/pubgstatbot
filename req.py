import http.client
from pubgstats import *


player = ''

a = [1,2,3,4,5]
a[4] = 0
print(a.index(10))

players = []
names = ['crazy_','chris_p_bacon','mikepayne','mast0r_d','swordo']
conn = http.client.HTTPSConnection("pubgtracker.com", port=443)
conn.connect()
for name in names:
    conn.request("GET", '/api/profile/pc/'+name, headers={'TRN-Api-Key':'9c4b760c-b8bf-481f-a720-7a5d1c87870c'})
    response = conn.getresponse()
    res = response.read().decode("utf-8")
    data = json.loads(res)
    out = ''

    players.append(Pubgstats(data))

    for server in data['Stats']:
        for stat in data['Stats'][1]['Stats']:
            if stat['label'] == 'K/D Ratio':
                out = str(stat['ValueDec'])
        #print(server['Region'] + ':' + server['Match'] +  ' - K/D Ratio: ' + out + '\n')




def table(players,srv,match,stat):

    table = dict()
    tab = []
    for player in players:
        table[player.getname()] = player.stat(srv, match, stat)

    ordered_table = sorted(table, key=table.__getitem__)
    for i, x in enumerate(ordered_table[::-1]):
        tab.append(str(i+1) + '. ' + x + ' - ' + str(table[x]))
    return tab



srv = 'agg'
match = 'squad'
stat = 'Move Distance Pg'

def seasons(players):
    seas = []
    for p in players:
        seas = seas + p.agg.seasons
    return sorted(set(seas))

print(seasons)

#print(table(players,srv,match,stat))

conn.close()