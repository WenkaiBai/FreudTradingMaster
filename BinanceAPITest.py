from TradingPlatform.Binance import Binance
import logging

logging.basicConfig(level=logging.DEBUG)
Binance.buy('BNB', 'USDT', 1)

