from tinydb import TinyDB, Query
import datetime
import ujson


class NoDataError(Exception):
    pass


class Tinypubgdb:
    def __init__(self, path, miner):
        self.db = TinyDB(path)
        self.seasons = self.db.table('seasons')
        self.subs = self.db.table('subscriptions', cache_size=None)
        self.regs = ['eu', 'na', 'as', 'sa', 'agg']
        self.matches = ['solo', 'duo', 'squad']
        self.miner = miner
        self.statidx = {'k/d ratio': 1,
                        'win %': 2,
                        'time survived': 3,
                        'rounds played': 4,
                        'wins': 5,
                        'win top 10 ratio': 5,
                        'top 10s': 6,
                        'top 10 ratio': 7,
                        'losses': 8,
                        'rating': 9,
                        'best rating': 10,
                        'damage pg': 11,
                        'headshot kills pg': 12,
                        'heals pg': 13,
                        'kills pg': 14,
                        'move distance pg': 15,
                        'revives pg': 16,
                        'road kills pg': 17,
                        'team kills pg': 18,
                        'time survived pg': 19,
                        'top 10s pg': 20,
                        'kills': 21,
                        'assists': 22,
                        'suicides': 23,
                        'team kills': 24,
                        'headshot kills': 25,
                        'headshot kill ratio': 26,
                        'vehicle destroys': 27,
                        'road kills': 28,
                        'daily kills': 29,
                        'weekly kills': 30,
                        'round most kills': 31,
                        'max kill streaks': 32,
                        'days': 33,
                        'longest time survived': 34,
                        'most survival time': 35,
                        'avg survival time': 36,
                        'win points': 37,
                        'walk distance': 38,
                        'ride distance': 39,
                        'move distance': 40,
                        'avg walk distance': 41,
                        'avg ride distance': 42,
                        'longest kill': 43,
                        'heals': 44,
                        'revives': 45,
                        'boosts': 46,
                        'damage dealt': 47,
                        'knock outs': 48,
                        'speed': 49,
                        'rambo score': 50,
                        'kills per hour': 51,
                        'damage per kill': 52}
        self.allstats = [x.lower() for x in ['K/D Ratio', 'Win %', 'Time Survived', 'Rounds Played', 'Wins', 'Win Top 10 Ratio', 'Top 10s', 'Top 10 Ratio', 'Losses', 'Rating', 'Best Rating', 'Damage Pg', 'Headshot Kills Pg', 'Heals Pg', 'Kills Pg', 'Move Distance Pg', 'Revives Pg', 'Road Kills Pg', 'Team Kills Pg', 'Time Survived Pg', 'Top 10s Pg', 'Kills', 'Assists', 'Suicides', 'Team Kills', 'Headshot Kills', 'Headshot Kill Ratio', 'Vehicle Destroys', 'Road Kills', 'Daily Kills', 'Weekly Kills', 'Round Most Kills', 'Max Kill Streaks', 'Days', 'Longest Time Survived', 'Most Survival Time', 'Avg Survival Time', 'Win Points', 'Walk Distance', 'Ride Distance', 'Move Distance', 'Avg Walk Distance', 'Avg Ride Distance', 'Longest Kill', 'Heals', 'Revives', 'Boosts', 'Damage Dealt', 'Knock outs', 'speed', 'rambo score', 'kills per hour', 'damage per kill']]
        self.regs = ['eu', 'na', 'as', 'sa', 'agg']
        self.matches = ['solo', 'duo', 'squad']

    def update(self, forced=False):
        names = self.getsubscribers()
        player_tables = [self.db.table(y) for y in names]
        uptodate = [x.contains(Query().timestamp == str(datetime.date.today())) for x in player_tables]
        self.miner.connect()
        for utd, name in zip(uptodate, names):
            if utd and not forced:
                continue

            data = ujson.loads(self.miner.getdata(name))

            if data['defaultSeason'] == self.getcurrentseason():
                entry = self.build_entry(data)
                player_table = self.db.table(name.lower(), cache_size=None)
                if utd and forced:
                    elem = player_table.get(Query().timestamp == str(datetime.date.today()))
                    player_table.remove(eids=[elem.eid])

                player_table.insert(entry)
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
                            return m['Stats'][self.statidx[st.lower()]]['value']
            raise NoDataError('No Data for ' + st)

        self.update()
        vals = []
        p_table = self.db.table(player.lower())
        if len(p_table) < 1:
            return 0
        elem = p_table.get((Query().timestamp == str(datetime.date.today())) & (Query().season == season))
        entrys = [dict(elem)]
        if elem.eid > 1:
            for i in range(elem.eid-1):
                if p_table.contains(eids=[elem.eid-i-1]):
                    entrys.append(dict(p_table.get(eid=elem.eid-i-1)))
                    break

        for e in entrys:
            if stat.lower() == "speed":  # in km/h
                distance = getstatfromelem(e, srv, match, "walk distance")
                time = getstatfromelem(e, srv, match, "time survived")
                time_on_ride = getstatfromelem(e, srv, match, "ride distance") / 80  # km/h
                value = (distance * 3.6) / (time - time_on_ride)

            elif stat.lower() == "rambo score":
                distance = getstatfromelem(e, srv, match, "walk distance")
                time = getstatfromelem(e, srv, match, "time survived")
                time_on_ride = getstatfromelem(e, srv, match, "ride distance") / 80  # km/h
                kills = getstatfromelem(e, srv, match, "kills")
                value = ((distance / 1000) * kills) / (((time - time_on_ride) / 3600) * (time / 3600))

            elif stat.lower() == "kills per hour":
                time = getstatfromelem(e, srv, match, "time survived")
                kills = getstatfromelem(e, srv, match, "kills")
                value = kills / (time / 3600)

            elif stat.lower() == "damage per kill":
                damage = getstatfromelem(e, srv, match, "damage dealt")
                kills = getstatfromelem(e, srv, match, "kills")
                value = damage / kills

            else:
                value = getstatfromelem(e, srv, match, stat)

            if value is None:
                vals.append(0)
            else:
                vals.append(value)

        if len(vals) > 1:
            vals.append(vals[0]-vals[1])

        return vals

    def progression(self, player, srv, match, stat, season):

        def tointtimestamp(dt):
            naive = dt.replace(tzinfo=None)
            epoch = datetime.datetime(1970, 1, 1, tzinfo=None)
            integer_timestamp = (naive - epoch) // datetime.timedelta(days=1)
            return integer_timestamp

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
                            if len(m) < 1:
                                continue
                            x.append(m['Stats'][self.statidx[stat.lower()]]['value'])
                            y.append(tointtimestamp(datetime.datetime.strptime(e['timestamp'], '%Y-%m-%d')))
                            y_labels.append(e['timestamp'])
        if len(x) < 1 or len(y) < 1 or len(y_labels) < 1:
            raise NoDataError
        return x, y, y_labels

    def unsubscribe(self, n):
        if not self.subs.contains(Query().name == n.lower()):
            raise Exception('Player ' + n + ' has never been subscribed')
        if self.subs.search((Query().active == False) & (Query().name == n.lower())):
            raise Exception('Player ' + n + ' is already unsubscribed')
        self.subs.update({'active': False}, Query()['name'].lower() == n.lower() )
        return True
