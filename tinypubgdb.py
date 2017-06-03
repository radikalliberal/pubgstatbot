from tinydb import TinyDB, Query
import datetime
import ujson

class Tinypubgdb:
    def __init__(self, path, miner):
        self.db = TinyDB(path)
        self.seasons = self.db.table('seasons')
        self.subs = self.db.table('subscriptions', cache_size=None)
        self.regs = ['eu', 'na', 'as', 'sa', 'agg']
        self.matches = ['solo', 'duo', 'squad']
        self.miner = miner

    '''Diese Methode sollte einmal am Tag aufgerufen werden damit neue Stats von Pubgtracker.com abgerufen werden
    und in der Datenbank aktualisiert werden'''
    def update(self):
        names = self.getsubscribers()
        player_tables = [self.db.table(y) for y in names]
        uptodate = [x.contains(Query().timestamp == str(datetime.date.today())) for x in player_tables]
        self.miner.connect()
        for utd, name in zip(uptodate,names):
            if utd:
                continue
            data = ujson.loads(self.miner.getdata(name))
            entry = self.build_entry(data)
            player_table = self.db.table(name.lower(), cache_size=None)
            player_table.insert(entry)
            print(entry)
            if not self.seasons.contains(Query().name == entry['season']):
                self.seasons.insert({'name':entry['season']})

        self.miner.close()

    def build_entry(self, json_obj):
        temp = dict()
        temp['timestamp'] = str(datetime.date.today())
        temp['season'] = json_obj['defaultSeason']
        temp['Region'] = []
        for r in self.regs:
            region = dict()
            region['name'] = r
            region['match'] = []
            for m in self.matches:
                match = dict()
                match['name'] = m
                match['Stats'] = []
                for st in json_obj['Stats']:

                    if st['Region'] == r and st['Season'] == json_obj['defaultSeason'] and st['Match'] == m:
                        for stat in st['Stats']:
                            s = {'label': stat['label'], 'value': float(stat['value']),
                                 'percentile': stat['percentile']}
                            match['Stats'].append(s)
                region['match'].append(match)
            temp['Region'].append(region)

        return temp

    def getseasons(self):
        return [seas['name'] for seas in self.seasons.all()]

    def getcurrentseason(self):
        return max([seas['name'] for seas in self.seasons.all()])

    def subscribe(self, name):
        if self.subs.search(Query().name.lower() == name.lower()):
            if self.subs.search((Query().name.lower() == name.lower()) & (Query().active == False)):
                self.subs.update({'active':True},Query().name.lower() == name.lower())
            elif self.subs.search((Query().name.lower() == name.lower()) & (Query().active == True)):
                raise Exception('Spieler ist bereits subscribed')
            return
        self.miner.connect()
        res = self.miner.getdata(name)
        data = ujson.loads(res)
        self.miner.close()
        if data['AccountId'] is None:
            raise NameError('Spielername nicht bei pubgtracker.com vorhanden')
        else:
            self.subs.insert({'name':name.lower(),'AccountId':data['AccountId'],'Avatar':data['Avatar'],'active':True})
            self.update()

    def getsubscribers(self):
        return [entry['name'] for entry in self.subs.search(Query().name.matches('.*')) if entry['active']]

    def stat(self, player, srv, match, stat, season):
        p_table = self.db.table(player.lower())
        if len(p_table) < 1:
            return 0
        entry = dict(p_table.get((Query().timestamp == str(datetime.date.today())) & (Query().season == season)))
        if entry is None:
            return 0
        for r in entry['Region']:
            if r['name'].lower() == srv.lower():
                for m in r['match']:
                    if m['name'].lower() == match.lower():
                        for s in m['Stats']:
                            if s['label'].lower() == stat.lower():
                                return s['value']
        return 0


    def progression(self, player, srv, match, stat, season):

        def tointtimestamp(dt):
            naive = dt.replace(tzinfo=None)
            epoch = datetime.datetime(1970, 1, 1, tzinfo=None)
            integer_timestamp = (naive - epoch) // datetime.timedelta(days=1)
            return integer_timestamp

        print(self.db.tables())

        if player.lower() not in self.db.tables():
            raise Exception('Spieler ' + player + ' nicht in Datenbank vorhanden')
            return

        p_table = self.db.table(player.lower())
        entry = p_table.search((Query().season == season))
        x, y , y_labels = [], [], []
        for e in entry:
            for r in e['Region']:
                if r['name'].lower() == srv.lower():
                    for m in r['match']:
                        if m['name'].lower() == match.lower():
                            for s in m['Stats']:
                                if s['label'].lower() == stat.lower():
                                    x.append(s['value'])
                                    y.append(tointtimestamp(datetime.datetime.strptime(e['timestamp'], '%Y-%m-%d')))
                                    y_labels.append(e['timestamp'])
        return x, y, y_labels

    def unsubscribe(self, n):
        if not self.subs.contains(Query().name.lower() == n.lower()):
            raise Exception('Spieler war nie subscribed')
        if self.subs.search((Query().active == False) & (Query().name.lower() == n.lower())):
            raise Exception('Spieler ist bereits unsubscribed')
        self.subs.update({'active':False},Query()['name'].lower() == n.lower() )
        return True
