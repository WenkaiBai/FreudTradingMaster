import logging
import sys
 
logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s][%(process)d:%(thread)d][%(levelname)s] %(message)s',
        filename="main.log",
        filemode='a+')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('[%(asctime)s][%(process)d:%(thread)d][%(levelname)s] %(message)s'))
logger = logging.getLogger(__name__)
logger.addHandler(console)

from binance.client import BinanceRESTAPI
import time


class Binance:
    lotSize = {'BTC': 6, 'BNB': 2, 'DASH': 5, 'ETH': 5, 'LTC': 5, 'BCHABC': 5, 'TUSD': 2, \
            'PAX' : 2, 'ERD' : 0, 'XMR':3, 'EOS':2, 'ATOM':3, 'USDC':2, 'NEO':3, 'ZEC' : 5}
    lotSize_smbl = {'LTCBTC' : 2, 'ETHBTC' :3, 'BCHABCBTC': 3}
    # item is coin type we want to buy, ex: BTC
    # base is coin we use to buy, ex: USDT
    # base amount is how much base coins we are going to use to buy item coin
    #  This buying operation is blocked until order finish
    # return: (real spend base amount, real bought item amount)

    apiKey = ''
    secretKey = ''
    @classmethod
    def buy(self, item, base, itemAmount, target_price = None):
        # item = btc, base = usdt, item a
        restClient = BinanceRESTAPI(Binance.apiKey, Binance.secretKey)

        price = None
        if target_price:
            price = target_price
        else:
            # get current price
            price = Binance.current_price(item, base, restClient)
            logger.debug("Current price is %s", price)
            print("Current price is %s" % price)

        # check if binance account has enough baseAmount
        balance = Binance.balance(base, restClient)
        logger.debug("Current balance is %s", balance)
        print("Current balance is %s" % balance)
        if balance == 0.0:
            # no enough balance, cannot proceed buying
            logger.error("there is no balance in account!")
            return -1
        elif balance < itemAmount * price:
            # we try best to buy as many as we can
            logger.error("we want to buy %f %s (which need %f), but only have %f", itemAmount, item, itemAmount * price, balance)
            return -1

        # create order and get order id
        logger.info('we are going to buy when price is ' + str(price))
        lotsize = Binance.lotSize_smbl[item+base] if item+base in Binance.lotSize_smbl else Binance.lotSize[item]
        order = restClient.new_order(item+base, "BUY", "LIMIT", "GTC", round(itemAmount, lotsize), price)
        logger.info('order information %s ', str(order.__dict__))

        # check order status until it finish and get total bought item
        tolerance_times = 0
        while True:
            try:
                order = restClient.query_order(symbol=item+base, order_id=order.id, orig_client_order_id=order.client_order_id)
            except Exception as e:
                logger.error(e.message)
                continue

            if order.status == 'NEW':
                logger.debug("Current order.status is %s", order.status)
                print("Current order.status is %s" % order.status)
                tolerance_times += 1
                if tolerance_times > 5:
                    rest = restClient.cancel_order(symbol = item+base, order_id = order.id, orig_client_order_id=order.client_order_id)
                    return -1
                continue

            if order.status == 'PARTIALLY_FILLED':
                # cancel
                rest = restClient.cancel_order(symbol = item+base, order_id = order.id, orig_client_order_id=order.client_order_id)
                print rest.__dict__
                continue

            if order.status == 'CANCELED':
                return 0

            # order finish
            if order.status == 'FILLED':
                logger.info("Buying order finish!")
                return 0
            else:
                # order failed.
                logger.error("order fails %s", order.__dict__)
                return -1

    # itemAmount mean how much item we are going to sell
    # return (how much base we got, how much item we sell)
    @classmethod
    def sell(self, item, base, itemAmount, target_price = None):
        restClient = BinanceRESTAPI(Binance.apiKey, Binance.secretKey)

        price = None
        if target_price:
            price = target_price
        else:
            # get current price
            price = Binance.current_price(item, base, restClient)
            logger.debug("Current price is %s", price)
            print("Current price is %s" % price)

        # check if binance account has enough baseAmount
        balance = Binance.balance(item, restClient)
        if balance == 0.0:
            # no enough balance, cannot proceed buying
            logger.error("there is no balance in account!")
            return -1
        elif balance < itemAmount:
            # we try best to buy as many as we can
            logger.info('got %.8f, need %.8f in balance', balance, itemAmount)
            itemAmount = balance
            #return -1

        # create order and get order id
        #logger.info('sell before %f', itemAmount)
        #itemAmount = round(round(itemAmount, Binance.lotSize[item]) / price, Binance.lotSize[base]) * price
        #logger.info('sell after %f', itemAmount)
        logger.info('we are going to sell when price is ' + str(price))
        logger.info('selling item amount %s ', str(itemAmount))
        lotsize = Binance.lotSize_smbl[item+base] if item+base in Binance.lotSize_smbl else Binance.lotSize[item]
        order = restClient.new_order(item+base, "SELL", "LIMIT", "GTC", round(itemAmount, lotsize), price)
        logger.info('order information %s ', str(order.__dict__))
        # check order status until it finish and get total bought item
        while True:
            try:
                order = restClient.query_order(symbol=item+base, order_id=order.id, orig_client_order_id=order.client_order_id)
            except Exception as e:
                logger.error(e.message)
                continue

            if order.status == 'PARTIALLY_FILLED' or order.status == 'NEW':
                time.sleep(0.005) #query order status every 2 seconds
                continue

            # order finish
            if order.status == 'FILLED':
                logger.info("Selling order finish!")
                return 0
                #return float(order.cummulative_quote_qty), float(order.executed_qty)
            else:
                # order failed.
                logger.error("order fails %s", order.__dict__)
                return -1

    @classmethod
    def balance(self, coin, restClient = None):
        if restClient is None:
            restClient = BinanceRESTAPI(Binance.apiKey, Binance.secretKey)

        # check if binance account has enough baseAmount
        account = restClient.account()
        for balance in account.balances:
            #print balance
            if balance.asset.lower() == coin.lower():
                return float(balance.free)

        return 0.0

    @classmethod
    def info(self, restClient = None):
        if restClient is None:
            restClient = BinanceRESTAPI(Binance.apiKey, Binance.secretKey)

        # check if binance account has enough baseAmount
        info = restClient.exchange_info()
        print info

        return 0.0
    
    @classmethod
    def get_coin_list(self, restClient = None):
        if restClient is None:
            restClient = BinanceRESTAPI(Binance.apiKey, Binance.secretKey)

        # check if binance account has enough baseAmount
        account = restClient.account()
        return map(lambda x: x.asset, account.balances)

    @classmethod
    def price_list(self, restClient = None):
        if restClient is None:
            restClient = BinanceRESTAPI(Binance.apiKey, Binance.secretKey)

        prices = restClient.new_all_prices()
        
        return map(lambda x: [x.symbol, x.price], prices)
        #for price in prices:
        #    print price
            #if price.symbol.lower() == symbol.lower():
            #    return float(price.price)

        #return -1
    @classmethod
    def price_ticker_list(self, restClient = None):
        if restClient is None:
            restClient = BinanceRESTAPI(Binance.apiKey, Binance.secretKey)

        prices = restClient.ticker()
        
        result = map(lambda x: [x.symbol, x.ask, x.bid], prices)
        for item in result:
            item[1].price = float(item[1].price)
            item[1].qty = float(item[1].qty)
            item[2].price = float(item[2].price)
            item[2].qty = float(item[2].qty)
        result = filter(lambda x: float(x[1].price) != 0 and float(x[2].price) != 0, result)
        return result


def seg_smbl(symbol, coin_list):
    coin2 = None
    for coin in coin_list:
        idx = symbol.find(coin)
        if idx == 0:
            coin, coin2 = coin, symbol[len(coin):]
            break
        elif idx > 0:
            coin, coin2 = symbol[:-len(coin)], coin
            break
    if coin2 in coin_list:
        return coin, coin2
    return None

def process_pair(client, pair1, pair2, against_pair):

    # step 1, buy pair1
    ask_pair1 = pair1[2]
    ask_pair2 = pair2[2]
    bid_against_pair = against_pair[2]
    total_price = ask_pair1.price * ask_pair1.qty
    # calc maximun pair2 value
    pair2_qty = total_price / ask_pair2.price
    
    actual_forward_amount = min(min(pair2_qty, ask_pair2.qty), bid_against_pair.qty)
    logger.info("pair2_wish_qty[%.8f], got qty [%.8f], against_amount [%.8f] and use [%.8f]",
            pair2_qty, ask_pair2.qty, bid_against_pair.qty, actual_forward_amount)
    
    target_qty = 30.0 / ask_pair1.price
    if ask_pair1.qty < target_qty or ask_pair2.qty < target_qty:
        logger.info("not enough 1")
        return
    if target_qty * ask_pair2.price > bid_against_pair.qty:
        logger.info("not enough 2")
        return

    #minLotTarget = Binance.lotSize[pair1[0]]
    #minLotBase = Binance.lotSize[pair1[1]]
    #minLotAgainst = Binance.lotSize[pair2[1]]

    res = client.buy(pair1[0], pair1[1], target_qty, ask_pair1.price)
    if res != 0:
        raise Exception('1')
    res = client.sell(pair2[0], pair2[1], target_qty, ask_pair2.price)
    if res != 0:
        raise Exception('2')
    res = client.sell(against_pair[0], against_pair[1], target_qty * ask_pair2.price, bid_against_pair.price)
    if res != 0:
        raise Exception('3')

    sys.exit(0)

if __name__ == '__main__':

    #formatter = logger.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    client = Binance()
    #client.info()
    #sys.exit(0)
    #client.buy('BTC', 'USDT', 0.0015, 12549)
    while True:
        logger.warning("begin probe...")
        coin_list = client.get_coin_list()
        coin_list = set(coin_list)
        price_list = client.price_ticker_list()

        price_list_dict = {}
        for smbl, ask, bid in price_list:
            price_list_dict[smbl] = [ask, bid]

        for smbl, ask_price, bid_price in price_list:
            result = seg_smbl(smbl, coin_list)
            if not result:
                continue
            coin1, coin2 = result # p1
            # find a third one
            for coin3 in coin_list:
                if coin3 == coin1 or coin3 == coin2:
                    continue
                # ask > bid
                if coin2 != 'USDT':
                    continue
                if coin1 + coin3 in price_list_dict and coin3 + coin2 in price_list_dict:
                    ask_price2, bid_price2 = price_list_dict[coin1 + coin3] # p2
                    ask_price3, bid_price3 = price_list_dict[coin3 + coin2] # p3

                    ratio = float(bid_price2.price) * float(bid_price3.price) - float(ask_price.price) #- 3 * ask_price.price * 0.00075
                    if ratio > 0.005:
                        logger.info("hit match %s", ' '.join(map(str, [coin1 + coin2, ask_price, \
                                coin1 + coin3, bid_price2, \
                                coin3 + coin2, bid_price3, ratio, 1])))
                        process_pair(client, [coin1, coin2, ask_price], [coin1, coin3, bid_price2], [coin3, coin2, bid_price3])

                    ratio =  - float(ask_price2.price) * float(ask_price3.price) + float(bid_price.price) #- 3 * bid_price.price * 0.00075
                    if ratio > 0.005:
                        logger.info("hit match %s", ' '.join(map(str, [coin1 + coin2, bid_price, \
                                coin1 + coin3, ask_price2, \
                                coin3 + coin2, ask_price3, ratio, -1])))
        time.sleep(0.02) 

