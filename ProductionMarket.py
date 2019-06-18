from Entity.Price import Price
from LongtermStrategy import  LongtermStrategy
from ShortTermStrategy import ShortTermStrategy
from Data.DataRetriever import DataRetriever
import logging
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from WeChat import WeChat

class ProductionMarket:
    def __init__(self):
        self.dataRetriever = DataRetriever()
        prices = self.dataRetriever.retrieveHistoricalData('2019-01-01')
        logging.debug("history data: %s", prices)
        self.commandCenter = ShortTermStrategy(prices)

        corpid = "ww2baed54bbccc5f0c"
        secret = "7K7XwCgZlj01W0jh7gqiJjvVKaSUOgQbm5rKf1MyJRU"
        agentid = "1000002"
        self.wechat = WeChat(corpid, secret, agentid)

    def action(self):
        current = self.dataRetriever.retrieveLastHourData()

        decision = self.commandCenter.do(current)
        logging.error(decision)

        if decision.Type == 'Quit with benefit' or decision.Type == 'First Position' \
                or decision.Type == "Stop with loss" or decision.Type == 'Follow Buying':
    
            logging.error(current)

            self.wechat.send_message(str(decision))

def tick(market):
    market.action()

def main():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s  %(filename)s : %(levelname)s  %(message)s',
                        datefmt  = '%Y-%m-%d %A %H:%M:%S')

    market = ProductionMarket()

    scheduler = BlockingScheduler()
    scheduler.add_job(tick, 'interval', [market], seconds=3600)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == '__main__':
    main()
