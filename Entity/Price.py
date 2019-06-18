class Price:
    def __init__(self, h, l, o, c, d = None):
        self.high = h
        self.low = l
        self.open = o
        self.close = c
        self.date = d

    def __str__(self):
        return "high: %s, low: %s, open: %s, close: %s, date: %s" % (self.high, self.low, self.open, self.close, self.date)

    def __repr__(self):
        return "[high: %s, low: %s, open: %s, close: %s, date: %s]" % (self.high, self.low, self.open, self.close, self.date)