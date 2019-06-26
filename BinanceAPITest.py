from TradingPlatform.Binance import Binance
import logging

def main():
    logging.basicConfig(level=logging.DEBUG)
    #Binance.buy('BTC', 'USDT', 30)
    Binance.sell('BNB', 'USDT', 2)

if __name__ == '__main__':
    main()
