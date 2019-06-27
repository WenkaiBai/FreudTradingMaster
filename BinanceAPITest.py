from TradingPlatform.Binance import Binance

def main():
    #Binance.buy('BTC', 'USDT', 30)
    Binance.sell('BNB', 'USDT', 0.001)

if __name__ == '__main__':
    main()
