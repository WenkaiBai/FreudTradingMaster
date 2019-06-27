from TradingPlatform.Binance import Binance
import logging
import sys

def main():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    #Binance.buy('BTC', 'USDT', 30)
    Binance.sell('BTC', 'USDT', 0.001)

if __name__ == '__main__':
    main()
