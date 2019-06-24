class Position:
    def __init__(self, buyingPrice, spend, index):
        self.buyingPrice = buyingPrice #USD
        self.spend = spend #USDT
        self.index = index
        self.amount = 0 #BTC
