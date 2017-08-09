import http.client
import datetime

class Pubgdataminer:
    def __init__(self, api_key):
        self.conn = http.client.HTTPSConnection("pubgtracker.com", port=443)
        self.apikey = api_key

    def connect(self):
        self.conn.connect()

    def close(self):
        self.conn.close()

    def getdata(self, name):
        print('[{}] Request for {} send'.format(datetime.datetime.now(), name))
        self.conn.request("GET", '/api/profile/pc/' + name,
                          headers={'TRN-Api-Key': self.apikey})
        response = self.conn.getresponse()
        res = response.read().decode("utf-8")
        #print(res)
        print('[{}] Response for {}'.format(datetime.datetime.now(), name))
        return res
