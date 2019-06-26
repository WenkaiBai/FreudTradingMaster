from binance.client import BinanceRESTAPI
import time
import logging

class Binance:
    lotSize = {'BTC' : 6, 'BNB' : 2}    
    # item is coin type we want to buy, ex: BTC
    # base is coin we use to buy, ex: USDT
    # base amount is how much base coins we are going to use to buy item coin
    #  This buying operation is blocked until order finish
    # return: (real spend base amount, real bought item amount)
    @classmethod
    def buy(self, item, base, baseAmount):
        restClient = BinanceRESTAPI(Binance.apiKey, Binance.secretKey)

        # check if binance account has enough baseAmount
        balance = Binance.balance(base, restClient)
        logging.debug("Current balance is %s", balance)
        print("Current balance is %s" % balance)
        if balance == 0.0:
            # no enough balance, cannot proceed buying
            logging.error("there is no balance in account!")
            return 0.0, 0.0
        elif balance < baseAmount:
            # we try best to buy as many as we can
            baseAmount = balance

        # get current price
        price = Binance.current_price(item, base, restClient)
        logging.debug("Current price is %s", price)
        print("Current price is %s" % price)
        # create order and get order id
        logging.info('we are going to buy when price is ' + str(price))
        order = restClient.new_order(item+base, "BUY", "LIMIT", "GTC", round(baseAmount/price, Binance.lotSize[item]), 10000)

        # check order status until it finish and get total bought item
        while True:
            order = restClient.query_order(symbol=item+base, order_id=order.id, orig_client_order_id=order.client_order_id)
            if order.status == 'PARTIALLY_FILLED' or order.status == 'NEW':
                logging.debug("Current order.status is %s", order.status)
                print("Current order.status is %s" % order.status)
                time.sleep(2) #query order status every 2 seconds
                continue

            # order finish
            if order.status == 'FILLED':
                logging.info("Buying order finish!")
                return float(order.cummulative_quote_qty), float(order.executed_qty)
            else:
                # order failed.
                logging.error("order fails %s", order.__dict__)
                return 0.0, 0.0

    # itemAmount mean how much item we are going to sell
    # return (how much base we got, how much item we sell)
    @classmethod
    def sell(self, item, base, itemAmount):
        restClient = BinanceRESTAPI(Binance.apiKey, Binance.secretKey)
        # check if binance account has enough baseAmount
        balance = Binance.balance(item, restClient)
        if balance == 0.0:
            # no enough balance, cannot proceed buying
            logging.error("there is no balance in account!")
            return 0.0, 0.0
        elif balance < itemAmount:
            # we try best to buy as many as we can
            itemAmount = balance

        # get current price
        price = Binance.current_price(item, base, restClient)

        # create order and get order id
        logging.info('we are going to sell when price is ' + str(price))
        order = restClient.new_order(item+base, "SELL", "LIMIT", "GTC", round(itemAmount, Binance.lotSize[item]), 50)

        # check order status until it finish and get total bought item
        while True:
            order = restClient.query_order(symbol=item+base, order_id=order.id, orig_client_order_id=order.client_order_id)
            if order.status == 'PARTIALLY_FILLED' or order.status == 'NEW':
                time.sleep(2) #query order status every 2 seconds
                continue

            # order finish
            if order.status == 'FILLED':
                logging.info("Selling order finish!")
                return float(order.cummulative_quote_qty), float(order.executed_qty)
            else:
                # order failed.
                logging.error("order fails %s", order.__dict__)
                return 0.0, 0.0

    @classmethod
    def balance(self, coin, restClient = None):
        if restClient is None:
            restClient = BinanceRESTAPI(Binance.apiKey, Binance.secretKey)

        # check if binance account has enough baseAmount
        account = restClient.account()
        for balance in account.balances:
            if balance.asset.lower() == coin.lower():
                return float(balance.free)

        return 0.0

    @classmethod
    def current_price(self, item, base, restClient = None):
        if restClient is None:
            restClient = BinanceRESTAPI(Binance.apiKey, Binance.secretKey)

        prices = restClient.all_prices()
        symbol = item+base

        for price in prices:
            if price.symbol.lower() == symbol.lower():
                return float(price.price)

        return -1

