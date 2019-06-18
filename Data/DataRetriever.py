import datetime
import pandas as pd
import numpy as np
import re
import requests
import json
from Entity.Price import Price

class DataRetriever:
    def retrieveLastHourData(self):
        URL = 'https://www.bitstamp.net/api/ticker_hour/'
        try:
            r = requests.get(URL)
            raw_body = json.loads(r.text)

            open = float(raw_body['open'])
            close = float(raw_body['last'])
            high = float(raw_body['high'])
            low = float(raw_body['low'])
            date = datetime.datetime.utcfromtimestamp(int(raw_body['timestamp'])).strftime('%Y-%m-%d')
            return Price(high, low, open, close, date)

        except requests.ConnectionError:
            print ("Error querying Bitstamp API")
        return None

    def retrieveHistoricalData(self, from_date, to_date=None, coin='bitcoin'):
        """Retrieve basic historical information for a specific cryptocurrency from coinmarketcap.com

        Parameters
        ----------
        from_date : the starting date (as string) for the returned data;
            required format is %Y-%m-%d (e.g. "2017-06-21")
        to_date : the end date (as string) for the returned data;
            required format is %Y-%m-%d (e.g. "2017-06-21")
            Optional. If unspecified, it will default to the current day
        coin : the name of the cryptocurrency (e.g. 'bitcoin', 'ethereum', 'dentacoin')

        Returns
        -------
        pandas Dataframe
        """
        if to_date is None:
            to_date = datetime.date.today().strftime("%Y-%m-%d")

        try:
            output = pd.read_html("https://coinmarketcap.com/currencies/{}/historical-data/?start={}&end={}".format(
                coin, from_date.replace("-", ""), to_date.replace("-", "")))[0]
        except:
            # future versions may split out the different exceptions (e.g. timeout)
            raise
        output = output.assign(Date=pd.to_datetime(output['Date']))
        for col in output.columns:
            if output[col].dtype == np.dtype('O'):
                output.loc[output[col] == "-", col] = 0
                output[col] = output[col].astype('int64')
        output.columns = [re.sub(r"[^a-z]", "", col.lower()) for col in output.columns]

        result = []
        for row in output.iterrows():
            open = float(row[1]['open'])
            close = float(row[1]['close'])
            high = float(row[1]['high'])
            low = float(row[1]['low'])
            date = row[1]['date'].strftime('%Y-%m-%d')
            result.insert(0, Price(high, low, open, close, date))
        return result

#dr = DataRetriever()
#o = dr.retrieveHistoricalData("2019-06-09")
#print(o)

#print(dr.retrieveLastHourData())
