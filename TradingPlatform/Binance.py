from binance.client import BinanceRESTAPI

class Binance:
    apiKey = 'a'
    secretKey = ''

    # item is coin type we want to buy, ex: BTC
    # base is coin we use to buy, ex: USDT
    # base amount is how much base coins we are going to use to buy item coin
    #  This buying operation is blocked until order finish
    #
    @classmethod
    def buy(self, item, base, baseAmount):
        restClient = BinanceRESTAPI(Binance.apiKey, Binance.apiKey)

        # check if binance account has enough baseAmount
        account = restClient.account()
        for coin in account.balances:
            if coin.asset.lower() == base.lower():
                balance = float(coin.free)
                if balance == 0.0:
                    # no enough balance, cannot proceed buying
                    return 0.0
                elif balance < baseAmount:
                    # we try best to buy as many as we can
                    baseAmount = balance
                break;

        # get current price


        # create order and get order id

        order = restClient.new_order(item+base, "BUY", "LIMIT", "GTC", baseAmount, '')

        # check order status until it finish and get total bought item

        # return bought item amount

    @classmethod
    def balance(self, coin):
        restClient = BinanceRESTAPI(Binance.apiKey, Binance.apiKey)

        # check if binance account has enough baseAmount
        account = restClient.account()
        for balance in account.balances:
            if balance.asset.lower() == coin.lower():
                return float(balance.free)


    @classmethod
    def current_price(self, coin):



Binance.buy(1, 2, 3)