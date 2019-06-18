import sys
import logging
from Entity.Position import Position
from Entity.Decision import Decision
from Entity.Price import Price

class LongtermStrategy:
    def __init__(self, prices, inTimeRange=55, outTimeRange=20):
        self.dailyPrices = prices
        self.inTimeRange = inTimeRange
        self.outTimeRange = outTimeRange

        self.balance = 10000.0 #USD
        self.positions = []
        self.N = self.initN()
        self.today = []

    def initN(self):
        N = []
        for i in range(1, len(self.dailyPrices)):
            H = self.dailyPrices[i].high
            L = self.dailyPrices[i].low
            PDC = self.dailyPrices[i-1].close
            TR = max(H-L, H-PDC, PDC-L)
            NLen = len(N)
            if NLen < 19:
                n= (sum(N) + TR) / (NLen + 1)
            else:
                n = (sum(N[NLen - 19 : NLen]) + TR) / 20

            N.append(n)
        logging.info("init N: %s", N)
        return N

    def calculateN(self, hourlyPrices):
        if len(hourlyPrices) == 0:
            logging.error("today prices is empty.")
            return self.N[-1]

        H = 0
        L = sys.maxsize
        PDC = self.dailyPrices[-1].close
        for hourlyPrice in hourlyPrices:
            if H < hourlyPrice.high:
                H = hourlyPrice.high

            if L > hourlyPrice.low:
                L = hourlyPrice.low

        TR = max(H-L, H-PDC, PDC-L)
        NLen = len(self.N)
        return (sum(self.N[NLen - 19 : NLen]) + TR) / 20

    def top(self):
        top = 0
        for price in self.dailyPrices[len(self.dailyPrices) - self.inTimeRange : -1]:
            if top < price.high:
                top = price.high
        logging.debug("top: %s", top)
        return top

    def bottom(self):
        bottom = sys.maxsize
        for price in self.dailyPrices[len(self.dailyPrices) - self.outTimeRange : -1]:
            if bottom > price.low:
                bottom = price.low

        logging.debug("bottom: %s", bottom)
        return bottom

    def dayPriceFromHourPrice(self, hours):
        h = 0
        l = sys.maxsize
        o = 0
        c = hours[-1].close

        for hour in hours:
            if o == 0:
                o = hour.open
            if h < hour.high:
                h = hour.high
            if l > hour.low:
                l = hour.low
        return Price(h, l, o, c)


    def do(self, currentPrice, currentTime):
        # return positive means buy, negative mean sell. 0 means do nothing
        if currentTime < 0 or currentTime > 23:
            logging.error("Input time error:%s", currentTime)
            return Decision('SYSTEM_ERROR', 0)

        if currentTime == 0 and len(self.today) != 0:
            logging.debug("starting a new day.")
            N = self.calculateN(self.today)
            self.N.append(N)
            self.dailyPrices.append(self.dayPriceFromHourPrice(self.today))
            self.today.clear()

        self.today.append(currentPrice)
        N = self.calculateN(self.today)
        logging.debug("today N: %s", N)

        if len(self.positions) == 0:
            if self.balance <= 0:
                logging.error("Bankruptcy!")
                return Decision('Bankruptcy', 0)

            top = self.top()
            if (currentPrice.close > top):
                logging.info("break through 55 days highest!!, current balance: %s" , self.balance)
                #make break
                spend = self.balance * 0.25
                self.positions.append(Position(currentPrice.close, spend))
                self.balance -= spend
                return Decision('First Position', spend)

        elif len(self.positions) < 4 and (currentPrice.close - self.positions[-1].buyingPrice) >= (N/2):
            # Continue buying
            logging.info("continue buying position")
            self.positions.append(Position(currentPrice.close, self.positions[-1].spend))
            self.balance -= self.positions[-1].spend
            return Decision('Follow Buying', self.positions[-1].spend)

        elif len(self.positions) > 0 and currentPrice.close < self.bottom():
            # quit all positions and finish this round
            logging.info("selling all position")
            sell = 0.0
            for position in self.positions:
                sell += (position.spend/position.buyingPrice) * currentPrice.close
            self.balance += sell
            self.positions.clear()
            return Decision('Quit with benefit', -sell)

        elif len(self.positions) > 0:
            sell = 0
            for position in list(self.positions):
                if position.buyingPrice - currentPrice.close >= 2 * N:
                    sell += (position.spend / position.buyingPrice) * currentPrice.close
                    self.positions.remove(position)
            if sell != 0:
                logging.info("Stop loss, sell %s USD", sell)
                self.balance += sell
                return Decision('Stop with loss', -sell)

        logging.debug("nothing happen, keep monitoring.")
        return Decision('Watching', 0)