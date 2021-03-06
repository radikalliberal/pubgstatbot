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
                        'weapons acquired': 49,
                        'best rank': 50,
                        'avg dmg per match': 51}
        self.allstats = [x.lower() for x in ['K/D Ratio',
                                             'Win %',
                                             'Time Survived',
                                             'Rounds Played',
                                             'Wins',
                                             'Win Top 10 Ratio',
                                             'Top 10s',
                                             'Top 10 Rate',
                                             'Losses',
                                             'Rating',
                                             'Best Rating',
                                             'Damage Pg',
                                             'Headshot Kills Pg',
                                             'Heals Pg',
                                             'Kills Pg',
                                             'Move Distance Pg',
                                             'Revives Pg',
                                             'Road Kills Pg',
                                             'Team Kills Pg',
                                             'Time Survived Pg',
                                             'Top 10s Pg',
                                             'Kills',
                                             'Assists',
                                             'Suicides',
                                             'Team Kills',
                                             'Headshot Kills',
                                             'Headshot Kill Ratio',
                                             'Vehicle Destroys',
                                             'Road Kills',
                                             'Daily Kills',
                                             'Weekly Kills',
                                             'Round Most Kills',
                                             'Max Kill Streaks',
                                             'Days',
                                             'Longest Time Survived',
                                             'Most Survival Time',
                                             'Avg Survival Time',
                                             'Win Points',
                                             'Walk Distance',
                                             'Ride Distance',
                                             'Move Distance',
                                             'Avg Walk Distance',
                                             'Avg Ride Distance',
                                             'Longest Kill',
                                             'Heals',
                                             'Revives',
                                             'Boosts',
                                             'Damage Dealt',
                                             'Knock outs',
                                             'speed',
                                             'speed kills per hour',
                                             'kills per hour',
                                             'damage per kill',
                                             'revives per knock out',
                                             'boosts pg',
                                             'speed kills pg',
                                             'weapons acquired',
                                             'best rank',
                                             'avg dmg per match']]
        self.regs = ['eu', 'na', 'as', 'sa', 'agg']
        self.matches = ['solo', 'duo', 'squad']
        self.checkfornewseason()
        self.currentseason = self.getcurrentseason()
        self.uptodate = self.checkuptodate()

    @staticmethod
    def tointtimestamp(dt):
        epoch = datetime.datetime(1970, 1, 1, tzinfo=None)
        integer_timestamp = (dt - epoch) // datetime.timedelta(days=1)
        return integer_timestamp

    def lookatrankings(self, match, stat, season):
        def lookatrank(p, m, s, sea):
            entry = self.stat(p, m, s, sea)
            if entry is None:
                return 0
            for k in sorted(entry, reverse=True):
                return entry[k]

        msg = dict()
        statrank_table = self.db.table(stat, cache_size=None)
        if not statrank_table.contains(Query().match == match):
            statrank_table.insert({'name': '', 'value': 0, 'match': match})

        current_ranking = dict()
        for player in self.getsubscribers():
            if self.db.table(player).contains(Query().season == season):
                current_ranking[player] = lookatrank(player, match, stat, season)

        top1 = dict(name='', value= 0, match='')
        for key in current_ranking.keys():
            if current_ranking[key] is not None:
                if current_ranking[key] > top1['value']:
                    top1['value'] = current_ranking[key]
                    top1['name'] = key
                    top1['match'] = match

        el = None
        for element in statrank_table.all():
            if 'match' in element:
                if element['match'] == match:
                    el = element
            else:
                print('removed:' + str(element))
                statrank_table.remove(eids=[element.eid])
        if top1['value'] != el['value'] and el['name'] != top1['name']:
            statrank_table.remove(eids=[el.eid])
            statrank_table.insert(top1)
            msg = dict(player=top1['name'], match=match, stat=stat, value=top1['value'])
            print('{0} : {1}/{2} -> {3}'.format(top1['name'], match, stat, top1['value']))
        return msg

    def getplayerimage(self, player):
        elem = self.subs.get(Query().name == player.lower())
        return elem['Avatar']

    def scatterpubg(self, player, stat1, stat2, match, season, xtimes):
        x, y = [], []
        returnval = [x, y]
        stat = [stat1, stat2]
        for i in range(2):
            tmp = self.stat(player, match, stat[i], season)
            for k in range(xtimes):
                tstamp = str(self.tointtimestamp(datetime.datetime.today())-xtimes+k+1)
                if tstamp in tmp:
                    returnval[i].append(tmp[tstamp])
                else:
                    returnval[i].append(None)
        return x, y

    def checkuptodate(self, player=None):
        if player is None:
            names = self.getsubscribers()
            player_tables = [self.db.table(y) for y in names]
            try:
                uptodate_ = [dict(x.get(Query().season == self.currentseason)) for x in player_tables]
                value = [str(self.tointtimestamp(datetime.datetime.today())) in x['match'][0]['stat'][0] for x in uptodate_]
            except TypeError:
                return [False for _ in player_tables]

            return value
        else:
            player_table = self.db.table(player)
            uptodate_ = dict(player_table.get(Query().season == self.currentseason))
            return str(self.tointtimestamp(datetime.datetime.today())) in uptodate_['match'][0]['stat'][0]

    def update(self, name=None, forced=False):
        self.miner.connect()

        def update_(player):
            player_table = self.db.table(player.lower(), cache_size=None)
            while True:
                data = ujson.loads(self.miner.getdata(player))
                if 'error' in data:
                    print('Fehler bei der Anfrage von '.format(player))
                else:
                    break

            if data['defaultSeason'] == self.currentseason:
                elem = player_table.get(Query().season == self.currentseason)
                if elem is not None:
                    player_table.remove(eids=[elem.eid])
                else:
                    elem = {'season': self.currentseason, 'match': []}
                    for m in self.matches:
                        match = dict()
                        match['name'] = m
                        match['stat'] = []
                        elem['match'].append(match)

                entry = self.build_entry(data, elem)
                player_table.insert(entry)
            else:
                print('Spieler {} hat noch nicht in der aktuellen Saison gespielt'.format(player))

        if name is None:
            names = self.getsubscribers()
            for utd, name in zip(self.uptodate, names):
                print(name)
                if utd and not forced:
                    continue
                else:
                    update_(name)

        else:
            if self.checkuptodate(name) and not forced:
                return
            else:
                update_(name)

        self.miner.close()

    def build_entry(self, json_obj, elem):

        for m in elem['match']:
            for st_json in json_obj['Stats']:
                if st_json['Region'] == 'agg' and st_json['Season'] == self.currentseason and st_json['Match'] == m['name']:
                    for st_json_agg in st_json['Stats']:
                        tstamp = str(self.tointtimestamp(datetime.datetime.today()))
                        #print(self.statidx[st_json_agg['label'].lower()])
                        if self.statidx[st_json_agg['label'].lower()] > (len(m['stat'])-1):
                            m['stat'].append(
                                {tstamp: float(st_json_agg['value']), 'name': st_json_agg['label'].lower()})
                        else:
                            m['stat'][self.statidx[st_json_agg['label'].lower()]][tstamp] = float(st_json_agg['value'])

        return elem

    def getseasons(self):
        return [seas['name'] for seas in self.seasons.all()]

    def checkfornewseason(self):
        data = ujson.loads(self.miner.getdata('swordo'))
        if data['defaultSeason'] not in self.getseasons():
            self.seasons.insert({'name': data['defaultSeason']})

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
            elem = {'season': self.currentseason}
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
            try:
                for m in e['match']:
                    if m['name'] == ma:
                        #print('len(m["stat"]):' + str(len(m['stat'])))
                        #print('{}:{}'.format(st, self.statidx[st]))
                        #print(m)
                        if len(m['stat']) <= self.statidx[st]:
                            return None
                        temp = m['stat'][self.statidx[st]]
                        del temp['name']
                        return temp
                return None
            except TypeError as error:
                print(error)
                return None

        p_table = self.db.table(player.lower())
        if len(p_table) < 1:
            return None
        elem = p_table.get(Query().season == season)
        values = dict()
        # Todo: Hier können Stats auch noch leer sein ....
        if stat.lower() == "speed kills pg":  # in km/h
            distance = getstatfromelem(elem, match, "walk distance")
            time = getstatfromelem(elem, match, "time survived")
            time_on_ride = getstatfromelem(elem, match, "ride distance")  # km/h
            kills = getstatfromelem(elem, match, "kills")
            rounds = getstatfromelem(elem, match, "rounds played")
            if time is None:
                values = []
            else:
                for k in time.keys():
                    values[k] = (distance[k] * 3.6 * kills[k]) / ((time[k] - time_on_ride[k] / 80) * rounds[k])

        elif stat.lower() == "speed":  # in km/h
            distance = getstatfromelem(elem, match, "walk distance")
            time = getstatfromelem(elem, match, "time survived")
            time_on_ride = getstatfromelem(elem, match, "ride distance")  # km/h
            if time is None:
                values = []
            else:
                for k in time.keys():
                    values[k] = (distance[k] * 3.6) / (time[k] - time_on_ride[k] / 80)

        elif stat.lower() == "speed kills per hour":
            distance = getstatfromelem(elem, match, "walk distance")
            time = getstatfromelem(elem, match, "time survived")
            time_on_ride = getstatfromelem(elem, match, "ride distance")  # km/h
            kills = getstatfromelem(elem, match, "kills")
            if time is None:
                values = []
            else:
                for k in time.keys():
                    values[k] = ((distance[k] / 1000) * kills[k]) / (((time[k] - time_on_ride[k] / 80) / 3600) * (time[k] / 3600))

        elif stat.lower() == "kills per hour":
            time = getstatfromelem(elem, match, "time survived")
            kills = getstatfromelem(elem, match, "kills")
            if time is None:
                values = []
            else:
                for k in time.keys():
                    values[k] = kills[k] / (time[k] / 3600)

        elif stat.lower() == "damage per kill":
            damage = getstatfromelem(elem, match, "damage dealt")
            kills = getstatfromelem(elem, match, "kills")
            if damage is None:
                values = []
            else:
                for k in damage.keys():
                    if kills[k] == 0:
                        values[k] = 0
                    else:
                        values[k] = damage[k] / kills[k]

        elif stat.lower() == "revives per knock out":
            revives = getstatfromelem(elem, match, "revives")
            knockouts = getstatfromelem(elem, match, "knock outs")
            if revives is None:
                values = []
            else:
                for k in revives.keys():
                    if knockouts[k] == 0:
                        values[k] = 0
                    else:
                        values[k] = revives[k] / knockouts[k]

        elif stat.lower() == "boosts pg":
            boosts = getstatfromelem(elem, match, "boosts")
            rounds = getstatfromelem(elem, match, "rounds played")
            if boosts is None:
                values = []
            else:
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


