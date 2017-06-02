import json

class Pubgstats:
    def __init__(self, json):
        self.jsonobj = json
        self.na = Region(json, 'na')
        self.eu = Region(json, 'eu')
        self.sa = Region(json, 'sa')
        self.asia = Region(json, 'as')
        self.agg = Region(json, 'agg')

    def getname(self):
        return self.jsonobj['PlayerName']


    def stat(self, srv, match, stat, season):
        stats = []
        if srv == 'na':
            stats = self.na
        elif srv == 'eu':
            stats = self.eu
        elif srv == 'as':
            stats = self.asia
        elif srv == 'sa':
            stats = self.sa
        elif srv == 'agg':
            stats = self.agg

        return stats.getstat(stat, match, season)

class Region:
    def __init__(self, json_obj, str):
        self.jsonobj = json_obj
        self.seasons = self.getSeasons()
        self.solo  = self.getRegionStat(str, 'solo')
        self.duo   = self.getRegionStat(str, 'duo')
        self.squad = self.getRegionStat(str, 'squad')

    def getSeasons(self):
        try:
            return sorted(set([r['Season'] for r in self.jsonobj['Stats']]))
        except Exception as e:
            print(e)
            return

    def getRegionStat(self, reg, match):
        regios = [None,None,None,None,None]
        for r in self.jsonobj['Stats']:
            if r['Region'] == reg:
                if r['Match'] == match:
                    regios[self.seasons.index(r['Season'])] = r
        return regios

    def getmatch(self, str):
        if str.lower() == 'solo':
            return self.solo
        elif str.lower() == 'duo':
            return self.duo
        elif str.lower() == 'squad':
            return self.squad

    def getstat(self, stat, match, season):
        try:
            self.seasons.index(season)
            if self.getmatch(match)[self.seasons.index(season)]['Stats'] is None:
                return 0

            for sta in self.getmatch(match)[self.seasons.index(season)]['Stats']:
                if sta is None: return 0
                if sta['label'].lower() == stat.lower():
                    if sta['ValueDec'] is not None:
                        return sta['ValueDec']
                    elif sta['ValueInt'] is not None:
                        return sta['ValueInt']
                    else:
                        return 0
        except Exception as e:
            print(e)
            return 0

