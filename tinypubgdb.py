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
        self.statidx = {'k/d ratio': 0,
                        'win %': 1,
                        'time survived': 2,
                        'rounds played': 3,
                        'wins': 4,
                        'win top 10 ratio': 5,
                        'top 10s': 6,
                        'top 10 rate': 7,
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
        self.allstats = [x.lower() for x in ['K/D Ratio', 'Win %', 'Time Survived', 'Rounds Played', 'Wins', 'Win Top 10 Ratio', 'Top 10s', 'Top 10 Rate', 'Losses', 'Rating', 'Best Rating', 'Damage Pg', 'Headshot Kills Pg', 'Heals Pg', 'Kills Pg', 'Move Distance Pg', 'Revives Pg', 'Road Kills Pg', 'Team Kills Pg', 'Time Survived Pg', 'Top 10s Pg', 'Kills', 'Assists', 'Suicides', 'Team Kills', 'Headshot Kills', 'Headshot Kill Ratio', 'Vehicle Destroys', 'Road Kills', 'Daily Kills', 'Weekly Kills', 'Round Most Kills', 'Max Kill Streaks', 'Days', 'Longest Time Survived', 'Most Survival Time', 'Avg Survival Time', 'Win Points', 'Walk Distance', 'Ride Distance', 'Move Distance', 'Avg Walk Distance', 'Avg Ride Distance', 'Longest Kill', 'Heals', 'Revives', 'Boosts', 'Damage Dealt', 'Knock outs', 'speed', 'rambo score', 'kills per hour', 'damage per kill', 'revives per knock out', 'boosts pg']]
        self.regs = ['eu', 'na', 'as', 'sa', 'agg']
        self.matches = ['solo', 'duo', 'squad']
        self.uptodate = self.checkuptodate()

    @staticmethod
    def tointtimestamp(dt):
        epoch = datetime.datetime(1970, 1, 1, tzinfo=None)
        integer_timestamp = (dt - epoch) // datetime.timedelta(days=1)
        return integer_timestamp

    def lookatrankings(self, match, season):
        def lookatrank(p, m, s, sea):
            entry = self.stat(p, m, s, sea)
            for key in sorted(entry, reverse=True):
                return entry[key]
        msgs = []
        for stat in self.allstats:
            statrank_table = self.db.table(stat, cache_size=None)
            if not statrank_table.search(Query().name.exists()):
                statrank_table.insert({'name': '', 'value': 0})
            for player in self.getsubscribers():
                el = statrank_table.all()[0]
                value = lookatrank(player, match, stat, season)
                if value > el['value']:
                    statrank_table.remove(eids=[el.eid])
                    statrank_table.insert({'name': player, 'value': value})
                    if el['name'] != player:
                        msgs.append('{0} : {1}/{2} -> {3}'.format(player, match, stat, el['value']))
                        print('{0} : {1}/{2} -> {3}'.format(player, match, stat, el['value']))
        return msgs

    def checkuptodate(self):
        names = self.getsubscribers()
        player_tables = [self.db.table(y) for y in names]
        uptodate_ = [dict(x.get(Query().season == self.getcurrentseason())) for x in player_tables]
        value = [str(self.tointtimestamp(datetime.datetime.today())) in x['match'][0]['stat'][0] for x in uptodate_]
        self.uptodate = value
        return value

    def update(self, forced=False):

        names = self.getsubscribers()
        self.miner.connect()
        for utd, name in zip(self.uptodate, names):
            if utd and not forced:
                continue

            player_table = self.db.table(name.lower(), cache_size=None)
            data = ujson.loads(self.miner.getdata(name))

            if data['defaultSeason'] == self.getcurrentseason():
                elem = player_table.get(Query().season == self.getcurrentseason())
                entry = self.build_entry(data, elem)
                player_table.remove(eids=[elem.eid])
                player_table.insert(entry)

        self.miner.close()

    def build_entry(self, json_obj, elem):

        for m in elem['match']:
            for st_json in json_obj['Stats']:
                if st_json['Region'] == 'agg' and st_json['Season'] == self.getcurrentseason() and st_json['Match'] == m['name']:
                    for st_json_agg in st_json['Stats']:
                        tstamp = str(self.tointtimestamp(datetime.datetime.today()))
                        m['stat'][self.statidx[st_json_agg['label'].lower()]][tstamp] = float(st_json_agg['value'])

        return elem

    def getseasons(self):
        return [seas['name'] for seas in self.seasons.all()]

    def getcurrentseason(self):
        return max([seas['name'] for seas in self.seasons.all()])

    def subscribe(self, name):
        if self.subs.search(Query().name == name.lower()):
            if self.subs.search((Query().active == False) & (Query().name == name.lower())):
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
            player_table = self.db.table(name.lower(), cache_size=None)
            elem = {'season': self.getcurrentseason()}
            elem['match'] = []
            for m in self.matches:
                match = dict()
                match['name'] = m
                match['stat'] = []
                for st in self.allstats:
                    stat = {'name': st}
                    match['stat'].append(stat)
                elem['match'].append(match)
            player_table.insert(elem)
            self.update()

    def unsubscribe(self, n):
        if not self.subs.contains(Query().name == n.lower()):
            raise Exception('Player ' + n + ' has never been subscribed')
        if self.subs.search((Query().active == False) & (Query().name == n.lower())):
            raise Exception('Player ' + n + ' is already unsubscribed')
        self.subs.update({'active': False}, Query().name == n.lower())
        return True

    def getsubscribers(self):
        return [entry['name'] for entry in self.subs.search(Query().name.matches('.*')) if entry['active']]

    def convertstat(self, player, srv, match, stat, season):

        def getstatfromelem(elem, sr, ma, st):
            for r in elem['Region']:
                if r['name'].lower() == sr.lower():
                    for m in r['match']:
                        if m['name'].lower() == ma.lower():
                            if len(m['Stats']) > 0:
                                return m['Stats'][self.statidx[st.lower()]]['value']

        p_table = self.db.table(player.lower())
        if len(p_table) < 1:
            return 0
        entrys = p_table.search(Query().season == season)

        vals = {}
        for e in entrys:
            value = getstatfromelem(e, srv, match, stat)
            if value is not None:
                vals[str(self.tointtimestamp(datetime.datetime.strptime(e['timestamp'], '%Y-%m-%d')))] = value

        return vals

    def stat(self, player, match, stat, season):
        def getstatfromelem(e, ma, st):
            for m in e['match']:
                if m['name'] == ma:
                    temp = m['stat'][self.statidx[st]]
                    del temp['name']
                    return temp
            return None

        p_table = self.db.table(player.lower())
        if len(p_table) < 1:
            return 0
        elem = p_table.get(Query().season == season)
        values = dict()

        if stat.lower() == "speed":  # in km/h
            distance = getstatfromelem(elem, match, "walk distance")
            time = getstatfromelem(elem, match, "time survived")
            time_on_ride = getstatfromelem(elem, match, "ride distance")  # km/h
            for k in time.keys():
                values[k] = (distance[k] * 3.6) / (time[k] - time_on_ride[k] / 80)

        elif stat.lower() == "rambo score":
            distance = getstatfromelem(elem, match, "walk distance")
            time = getstatfromelem(elem, match, "time survived")
            time_on_ride = getstatfromelem(elem, match, "ride distance")  # km/h
            kills = getstatfromelem(elem, match, "kills")
            for k in time.keys():
                values[k] = ((distance[k] / 1000) * kills[k]) / (((time[k] - time_on_ride[k] / 80 ) / 3600) * (time[k] / 3600))

        elif stat.lower() == "kills per hour":
            time = getstatfromelem(elem, match, "time survived")
            kills = getstatfromelem(elem, match, "kills")
            for k in time.keys():
                values[k] = kills[k] / (time[k] / 3600)

        elif stat.lower() == "damage per kill":
            damage = getstatfromelem(elem, match, "damage dealt")
            kills = getstatfromelem(elem, match, "kills")
            for k in damage.keys():
                if kills[k] == 0:
                    values[k] = 0
                else:
                    values[k] = damage[k] / kills[k]

        elif stat.lower() == "revives per knock out":
            revives = getstatfromelem(elem, match, "revives")
            knockouts = getstatfromelem(elem, match, "knock outs")
            for k in revives.keys():
                if knockouts[k] == 0:
                    values[k] = 0
                else:
                    values[k] = revives[k] / knockouts[k]

        elif stat.lower() == "boosts pg":
            boosts = getstatfromelem(elem, match, "boosts")
            rounds = getstatfromelem(elem, match, "rounds played")
            for k in boosts.keys():
                if rounds[k] == 0:
                    values[k] = 0
                else:
                    values[k] = boosts[k] / rounds[k]

        else:
            values = getstatfromelem(elem, match, stat)

        return values

    def progression(self, player, match, stat, season):
        if player.lower() not in self.db.tables():
            raise Exception('Player ' + player + ' not found in database. \nYou have to subscribe (?subscribe %playername%) first, then statistics are tracked once a day')
            return

        p_table = self.db.table(player.lower())
        entry = p_table.get((Query().season == season))
        x, y, y_labels = [], [], []
        for m in entry['match']:
            if m['name'].lower() == match.lower():
                if len(m['stat']) < 1:
                    continue

                stats = self.stat(player, match, stat, season)
                x = [v for k, v in stats.items()]
                y = [int(k) for k, v in stats.items()]
                y_labels = [datetime.datetime.fromtimestamp(int(k)*24*60*60).strftime('%Y-%m-%d') for k, v in stats.items()]

        if len(x) < 1 or len(y) < 1 or len(y_labels) < 1:
            raise NoDataError
        return x, y, y_labels


