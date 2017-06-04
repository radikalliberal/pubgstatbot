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

    def update(self):
        names = self.getsubscribers()
        player_tables = [self.db.table(y) for y in names]
        uptodate = [x.contains(Query().timestamp == str(datetime.date.today())) for x in player_tables]
        self.miner.connect()
        for utd, name in zip(uptodate, names):
            if utd:
                continue
            data = ujson.loads(self.miner.getdata(name))
            if data['defaultSeason'] == self.getcurrentseason():
                entry = self.build_entry(data)
                player_table = self.db.table(name.lower(), cache_size=None)
                player_table.insert(entry)
                print(entry)
                if not self.seasons.contains(Query().name == entry['season']):
                    self.seasons.insert({'name': entry['season']})

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
        if self.subs.search(Query().name == name.lower()):
            if self.subs.search((Query().name == name.lower()) & (Query().active is False)):
                self.subs.update({'active': True}, Query().name == name.lower())
            elif self.subs.search((Query().name == name.lower()) & (Query().active is True)):
                raise Exception('Player ' + name + ' already subscribed')
            return
        self.miner.connect()
        res = self.miner.getdata(name)
        data = ujson.loads(res)
        self.miner.close()
        if data['AccountId'] is None:
            raise NameError('playername not existent at pubgtracker.com')
        else:
            self.subs.insert({'name': name.lower(),
                              'AccountId': data['AccountId'],
                              'Avatar': data['Avatar'],
                              'active': True})
            self.update()

    def getsubscribers(self):
        return [entry['name'] for entry in self.subs.search(Query().name.matches('.*')) if entry['active']]

    def stat(self, player, srv, match, stat, season):

        def getstatfromelem(elem, sr, ma, st):
            for r in elem['Region']:
                if r['name'].lower() == sr.lower():
                    for m in r['match']:
                        if m['name'].lower() == ma.lower():
                            for s in m['Stats']:
                                if s['label'].lower() == st.lower():
                                    return s['value']

        self.update()
        vals = []
        p_table = self.db.table(player.lower())
        if len(p_table) < 1:
            return 0
        elem = p_table.get((Query().timestamp == str(datetime.date.today())) & (Query().season == season))
        entrys = [dict(elem)]
        if elem.eid > 1:
            entrys.append(dict(p_table.get(eid=elem.eid-1)))

        for e in entrys:
            value = getstatfromelem(e, srv, match, stat)
            if value is None:
                vals.append(0)
            else:
                vals.append(value)

        print(player)
        print(entrys)
        print(type(vals))
        print(vals)
        if len(vals) > 1:
            vals.append(vals[0]-vals[1])

        return vals

    def progression(self, player, srv, match, stat, season):

        def tointtimestamp(dt):
            naive = dt.replace(tzinfo=None)
            epoch = datetime.datetime(1970, 1, 1, tzinfo=None)
            integer_timestamp = (naive - epoch) // datetime.timedelta(days=1)
            return integer_timestamp

        print(self.db.tables())

        if player.lower() not in self.db.tables():
            raise Exception('Player ' + player + ' not found in database. \nYou have to subscribe (?subscribe %playername%) first, then statistics are tracked once a day')
            return

        p_table = self.db.table(player.lower())
        entry = p_table.search((Query().season == season))
        x, y, y_labels = [], [], []
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
        if len(x) < 1 or len(y) < 1 or len(y_labels) < 0:
            return [0], [0], [0]
        return x, y, y_labels

    def unsubscribe(self, n):
        if not self.subs.contains(Query().name == n.lower()):
            raise Exception('Player ' + n + ' has never been subscribed')
        if self.subs.search((Query().active == False) & (Query().name == n.lower())):
            raise Exception('Player ' + n + ' is already unsubscribed')
        self.subs.update({'active': False}, Query()['name'].lower() == n.lower() )
        return True
