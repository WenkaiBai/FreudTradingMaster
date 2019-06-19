import tushare as ts
from Entity.Price import Price
from LongtermStrategy import  LongtermStrategy
from ShortTermStrategy import ShortTermStrategy
import logging
import datetime


def main():
	logging.basicConfig(level=logging.DEBUG)

	start = '2016-01-01'
	now = datetime.datetime(2018, 4, 1)
	totalBenefit = 0
	for i in range(1):
		now = now + datetime.timedelta(days=1)
		result = simulate(start, now)
		benefit = sum(result)
		totalBenefit += benefit
		if benefit < 0:
			logging.error(result)
	logging.error('average benfit: %s', totalBenefit/365)


def simulate(start, now):
    p = generateHistoricalData(start, now.strftime('%Y-%m-%d'))
    # commandCenter = LongtermStrategy(p)
    commandCenter = ShortTermStrategy(p)

    while now < datetime.datetime(2019, 4, 1):
        next = now + datetime.timedelta(days=1)
        data = ts.get_hist_data('cyb', start=now.strftime('%Y-%m-%d'), end=next.strftime('%Y-%m-%d'), ktype="5")[::-1]
        for row in data.iterrows():
            open = float(row[1]['open'])
            close = float(row[1]['close'])
            high = float(row[1]['high'])
            low = float(row[1]['low'])
            date = row[0].split(' ')[0]

            currentPrice = Price(high, low, open, close, date)

            decision = commandCenter.do(currentPrice)
            if decision.Type == 'Quit with benefit' or decision.Type == 'First Position' \
                    or decision.Type == "Stop with loss" or decision.Type == 'Follow Buying':
                logging.info(decision)
                logging.info(row)
        now = next
    return commandCenter.account


# Exclusive end Date
def generateHistoricalData(startDate, endDate):
    data = ts.get_hist_data('cyb', start=startDate, end=endDate, ktype="D")
    dailyPrices = []

    for row in data.iterrows():
        open = float(row[1]['open'])
        close = float(row[1]['close'])
        high = float(row[1]['high'])
        low = float(row[1]['low'])
        date = row[0]
        dailyPrices.insert(0, Price(high, low, open, close, date))

    return dailyPrices


if __name__ == '__main__':
    main()