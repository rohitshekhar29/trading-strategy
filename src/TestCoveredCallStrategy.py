# Your API token and GTLB symbol
import datetime
import requests

api_token = "ZHM2OUxMc0pIMU90YzNhQnY3bGY4Q3VWYmJvek10Umc0cnZpZGxPZE5MND0"
symbol = "SPY"
headers = {"Authorization": f"Bearer {api_token}"}

start_date = datetime.datetime(2023, 6, 2)
end_date = datetime.datetime(2023, 12, 29)
current = start_date
stock_count = 0
amount = 50000
initial_amount = amount
starting_stock_price = 380
sp = 0
delta = 1
edelta = 1

"""
for a given expiry and strike price
    if stock count is 0 then buy stock , if needed more money then use money
    get the premium at close of first day of the last week.
    get the stock price at expiry
        if out of money then add premium as profit
        if in money then sell the stock and profit is buying - selling + premium
        save the money in money bank
"""


def get_symbol(e, d):
    url = "https://api.marketdata.app/v1/options/lookup/" + symbol + "%20" + str(e.month) + "/" + str(
        e.day) + "/" + str(e.year) + "%20" + str(d) + "%20Call"
    response = requests.get(url, headers=headers)
    # response.raise_for_status()  # Raise an exception for error status codes
    data = response.json()
    if response.status_code == 200:
        return data['optionSymbol']
    return -1


def get_stock_price(dt, open=False):
    # url1 = "https://api.marketdata.app/v1/stocks/candles/D/AAPL?from=2023-12-28&to=2023-12-28&columns=c"
    column = 'c'
    if open:
        column = 'o'
    url = "https://api.marketdata.app/v1/stocks/candles/D/" + symbol + "?date=" + str(dt.date()) + "&columns=" + column
    response = requests.get(url, headers=headers)
    # response.raise_for_status()  # Raise an exception for error status codes
    data = response.json()
    if response.status_code == 200:
        return data[column][0]
    return -1


def get_initial_stock_price(exp):
    dt1 = exp - datetime.timedelta(days=delta)
    price = get_stock_price(dt1, open=True)
    while dt1 < exp and price == -1:
        dt1 = dt1 + datetime.timedelta(days=1)
        price = get_stock_price(dt1, open=True)
    return price, dt1


def get_option_price(exp1, sp1, dt1):
    try:
        option_symbol = get_symbol(exp1, sp1)
        # 'https://api.marketdata.app/v1/options/quotes/AAPL231229C00250000/?date=2023-12-2
        url = "https://api.marketdata.app/v1/options/quotes/" + option_symbol + "/?date=" + str(
            dt1.date()) + "&columns=last"
        response = requests.get(url, headers=headers)
        data = response.json()
        if response.status_code == 200:
            return data['last'][0]
    except:
        print(f"symbol: {option_symbol} date: {str(dt1.date())} sp: {sp1: .2f}")
    return -1


def purchase_stock(purse, expiry, bank):
    # get the stock price
    # find how many bundle can be bought
    # loan from bank if needed
    price, dt = get_initial_stock_price(expiry)
    if price <= 0:
        return 0, bank, -1, dt, purse
    count = purse / price
    count = int(count / 100)
    if count == 0:
        bank -= price * 100 - purse
        count = 1

    bank += max(0, purse - (price * count * 100))
    amount = price * count * 100

    return count, bank, price, dt, amount


def get_closest_sp_gt(price, expiry, dt):
    url = 'https://api.marketdata.app/v1/options/strikes/' + symbol + "/?date=" + str(dt.date()) + "&expiration=" + \
          str(expiry.date()) + "&columns=" + str(expiry.date())

    response = requests.get(url, headers=headers)
    data = response.json()
    if response.status_code != 200:
        return -1
    sps = data[str(expiry.date())]
    for s in sps:
        if s > price:
            return s
    return -1


def sell_call_premium(p1, exp1, price1, dt1):
    s = get_closest_sp_gt(price1, exp1, dt1)
    if price1 >= p1 and s > 0:
        op = get_option_price(exp1, s, dt1)
        return op, s
    return 0, 0


RBLX_skip = [datetime.datetime(2022, 2, 15), datetime.datetime(2022, 5, 10), datetime.datetime(2022, 8, 9), datetime.datetime(2022, 11, 9),
    datetime.datetime(2023, 2, 15), datetime.datetime(2023, 5, 10), datetime.datetime(2023, 8, 9),
        datetime.datetime(2023, 11, 8)]

APPL_skip = [datetime.datetime(2023, 2, 2), datetime.datetime(2023, 5, 4), datetime.datetime(2023, 8, 3), datetime.datetime(2023, 11, 2)]
skip = RBLX_skip

def skip_week(expr):
    for dt in skip:
        if expr > dt and dt > expr - datetime.timedelta(days=6):
            return True
    return False


def run():
    bank = 0
    global amount
    expiry = datetime.datetime(2023, 1, 1)
    end_date = datetime.datetime(2023, 12, 31)
    lot_count = 0
    price = 0
    dt = 0
    gain = 0
    best_amount = initial_amount
    global edelta, delta
    while expiry <= end_date:
        '''if skip_week(expiry):
            expiry = expiry + datetime.timedelta(days=7)
            continue'''

        #best_amount = max(best_amount, amount + bank + gain)
        if lot_count == 0:
            amount += bank
            bank = 0

            # when will this happen ?
            if amount+bank+gain < 0.9 * initial_amount:
                expiry = expiry + datetime.timedelta(days=edelta)
                print("exiting as we are done")
                continue
            lot_count, bank, price, dt, amount = purchase_stock(amount, expiry, bank)
            if lot_count <= 0:
                expiry = expiry + datetime.timedelta(days=edelta)
                continue
        else:
            price, dt = get_initial_stock_price(expiry)
            amount = lot_count * price * 100
            best_amount = max(best_amount, amount + bank + gain)
            if amount + bank + gain < 0.9 * initial_amount:
                expiry = expiry + datetime.timedelta(days=edelta)
                continue
        prem, strike_price = sell_call_premium(starting_stock_price, expiry, price, dt)
        if prem <= 0:
            print(
                f"expiry: {expiry.date()} amount: {amount: .2f} bank: {bank: .2f} stock: {price: .2f} prem: {prem: .2f} "
                f"count: {lot_count: .2f} sp: {strike_price: .2f} gain: {gain: .2f} "
                f"net: {amount + bank + gain: .2f}")
            expiry = expiry + datetime.timedelta(days=edelta)
            continue

        ending_stock_price = get_stock_price(expiry)
        sc = lot_count
        # print(ending_stock_price, strike_price, bank)
        # bank += (prem * sc * 100)
        gain += (prem * sc * 100)
        if float(ending_stock_price) > float(strike_price):
            print("sell")
            amount = strike_price * lot_count * 100 + bank
            lot_count = 0
            bank = 0
        print(f"expiry: {expiry.date()} amount: {amount: .2f} bank: {bank: .2f} stock: {price: .2f} "
              f"esp: {ending_stock_price: .2f} prem: {prem: .2f} "
              f"count: {sc: .2f} sp: {strike_price: .2f} gain: {gain: .2f}"
              f"net: {amount + bank + gain: .2f}")
        expiry = expiry + datetime.timedelta(days=edelta)


run()


'''
1. Buy 10 percent 12 weeks 
2. Maintain moving average 20 percent
    1. if stp is more than 20 percent then convert to closest 20 percent with expirt 3 months
    2. if stp is less than 9'
'''