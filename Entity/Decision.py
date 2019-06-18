class Decision:
    def __init__(self, t, o):
        self.Type = t
        self.Operation = o

    def __str__(self):
        return 'Type: %s, Operation: %s' % (self.Type, self.Operation)