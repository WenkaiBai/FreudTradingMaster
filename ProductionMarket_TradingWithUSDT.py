from Entity.Price import Price
from LongtermStrategy import  LongtermStrategy
from ShortTermStrategy import ShortTermStrategy
from ShortTermStrategy_TradingWithUSDT import ShortTermStrategy_TradingWithUSDT
from Data.DataRetriever import DataRetriever
import logging
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from WeChat import WeChat
from TradingPlatform.Binance import Binance

class ProductionMarket_TradingWithUSDT:


    def __init__(self):
        self.dataRetriever = DataRetriever()
        prices = self.dataRetriever.retrieveHistoricalData('2019-01-01')
        logging.debug("history data: %s", prices)
        #self.commandCenter = ShortTermStrategy(prices)
        self.commandCenter = ShortTermStrategy_TradingWithUSDT(prices)

        self.wechat = WeChat()

        self.base = 'USDT'
        self.item = 'BTC'

    def action(self):
        current = self.dataRetriever.retrieveLastHourData()

        decision = self.commandCenter.do(current)
        logging.error(decision)

        self.handleDecision(decision)

    def handleDecision(self, decision):
        if decision.Type.contains('Buy'):
            # Buying position
            position = decision.Operation

            self.wechat.send_message("Start buying posision: " + str(decision))
            base, item = Binance.buy(self.base, self.item, position.spend)
            self.wechat.send_message("Finish buying base: " + base)
            self.commandCenter.reduceBalance(base)
            position.spend = base
            position.amount = item
            logging.info("new Position is %s", position)
            self.commandCenter.updatePosition(position)
        else:
            # Selling position
            positions = decision.Operation
            baseAmount = 0.0
            itemAmount = 0.0
            for position in positions:
                itemAmount += position.amount
                baseAmount += position.spend

            self.wechat.send_message("Start selling itemAmount: " + str(itemAmount))
            base, item = Binance.sell(self.base, self.item, itemAmount)
            self.wechat.send_message("Finish selling base: " + str(base))
            self.commandCenter.supplementBalance(base)
            self.commandCenter.updatePerformance(base - baseAmount) # how much usdt we earn after selling


def tick(market):
    market.action()


def main():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s  %(filename)s : %(levelname)s  %(message)s',
                        datefmt  = '%Y-%m-%d %A %H:%M:%S')

    market = ProductionMarket_TradingWithUSDT()

    scheduler = BlockingScheduler()
    scheduler.add_job(tick, 'interval', [market], seconds=3600)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == '__main__':
    main()
