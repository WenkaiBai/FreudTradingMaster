import csv
from Entity.Price import Price
from LongtermStrategy import  LongtermStrategy
from ShortTermStrategy import ShortTermStrategy
import logging
import datetime

def main():
	logging.basicConfig(level=logging.ERROR)

	start = '2016-01-01'
	now = datetime.datetime(2018, 4, 1)
	totalBenefit = 0
	for i in range(365):
		now = now + datetime.timedelta(days=1)
		result = simulate(start, now.strftime('%Y-%m-%d'))
		benefit = sum(result)
		totalBenefit += benefit
		if benefit < 0:
			logging.error(result)
	logging.error('average benfit: %s', totalBenefit/365)

def simulate(start, now):
	p = generateHistoricalData(start, now)
	# commandCenter = LongtermStrategy(p)
	commandCenter = ShortTermStrategy(p)

	with open('resource/BTCUSD_1h.csv', newline='') as csvfile:
		reader = csv.DictReader(csvfile)
		cursor = 0
		for row in reader:
			date = row['Date'].split(' ')[0]
			if date < now:
				continue

			h = float(row['High'])
			l = float(row['Low'])
			o = float(row['Open'])
			c = float(row['Close'])
			currentPrice = Price(h, l, o, c)

			decision = commandCenter.do(currentPrice, cursor % 24)
			if decision.Type == 'Quit with benefit' or decision.Type == 'First Position' \
					or decision.Type == "Stop with loss" or decision.Type == 'Follow Buying':
				logging.info(decision)
				logging.info(row)
			cursor += 1

	return commandCenter.account

# Exclusive end Date
def generateHistoricalData(startDate, endDate):
	dailyPrices = []
	with open('resource/BTC-USD.csv', newline='') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			if row['Date'] < startDate:
				continue

			if row['Date'] >= endDate:
				break

			h = float(row['High'])
			l = float(row['Low'])
			o = float(row['Open'])
			c = float(row['Close'])
			p = Price(h, l, o, c)
			dailyPrices.append(p)

	return dailyPrices



if __name__ == '__main__':
	main()