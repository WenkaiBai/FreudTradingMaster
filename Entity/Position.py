class Position:
    def __init__(self, buyingPrice, spend, index):
        self.buyingPrice = buyingPrice #USD

        # this will update after trading because it may have some bias when real trading happend
        self.spend = spend #USDT

        # this will update after trading because it may have some bias when real trading happend
        self.amount = 0 #BTC

        self.index = index

    def __str__(self):
        return 'buyingPrice: %s, spend: %s, amount: %s, index: %s' % (self.buyingPrice, self.spend, self.amount, self.index)

    def __repr__(self):
        return 'buyingPrice: %s, spend: %s, amount: %s, index: %s' % (self.buyingPrice, self.spend, self.amount, self.index)
