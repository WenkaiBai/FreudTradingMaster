'''
lines = []
with open('resource/Exmo_BTCUSD_1h.csv', 'r') as src:
    for l in src:
        lines.append(l)

lines.reverse()
with open('resource/BTCUSD_1h.csv', 'w') as target:
    for i in range(len(lines)):
        target.write(lines[i])
'''

print ("2919-08-89 12 AM" == '2919-08-89 12 AM')
import logging
import sys

class Utility:
    @classmethod
    def top(self, prices, timeRange):
        top = 0
        for price in prices[len(prices) - timeRange: len(prices)]:
            if top < price.high:
                top = price.high
        logging.debug("top: %s", top)
        return top

    @classmethod
    def bottom(self, prices, timeRange):
        bottom = sys.maxsize
        for price in prices[len(prices) - timeRange: len(prices)]:
            if bottom > price.low:
                bottom = price.low

        logging.debug("bottom: %s", bottom)
        return bottom

    @classmethod
    def average(self, prices, timeRange):
        return sum([p.close for p in prices[len(prices) - timeRange: len(prices)]]) / timeRange