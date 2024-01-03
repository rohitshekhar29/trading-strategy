import pandas as pd
from datetime import datetime, timedelta


def calculate_weekly_profit(stock_prices, x_percent, a_percent, b_days, start_date, end_date):
    total_money = x_percent  # Initial investment amount
    remaining_money = total_money
    strike_percent = 1.03
    premium_percent = 0.4 / 100.0
    reinvest_percent = 50 / 100.0
    deposit = 0
    direction = True

    stocks_count = 0  # Initialize stocks_count based on initial investment
    stocks_count_prev = 0
    addn_amount = remaining_money

    current_date = start_date
    end_date_weekly = min(start_date + timedelta(days=b_days - 1), end_date)

    while current_date <= end_date:
        weekly_prices = stock_prices.loc[current_date:end_date_weekly]
        if len(weekly_prices) < 5:
            current_date += timedelta(weeks=1)
            end_date_weekly = min(current_date + timedelta(days=b_days - 1), end_date)
            continue
        week_open = weekly_prices['Open'].iloc[0]

        stocks_count = addn_amount / week_open
        stocks_count += stocks_count_prev
        addn_amount = 0

        week_close = weekly_prices['Close'].iloc[-1]
        strike_price = week_open * strike_percent
        premium = (strike_price * premium_percent)

        remaining_money = stocks_count * week_open

        if remaining_money < 1 * total_money:
            current_date += timedelta(weeks=1)
            end_date_weekly = min(current_date + timedelta(days=b_days - 1), end_date)
            continue

        if direction:
            if weekly_prices['Close'].iloc[-1] < strike_price:
                profit = premium * stocks_count
                addn_amount = profit / 2
                deposit += profit / 2
                stocks_count_prev = stocks_count
            else:
                profit = (strike_price - week_open + premium) * stocks_count
                remaining_money = (strike_price + premium) * stocks_count - profit / 2
                deposit += profit / 2
                stocks_count_prev = 0
                addn_amount = remaining_money
        else:
            if weekly_prices['Close'].iloc[-1] > strike_price:
                profit = premium * stocks_count
                addn_amount = profit / 2
                deposit += profit / 2
                stocks_count_prev = stocks_count
            else:
                profit = (strike_price - week_open + premium) * stocks_count
                remaining_money = (strike_price + premium) * stocks_count - profit / 2
                deposit += profit / 2
                stocks_count_prev = 0
                addn_amount = remaining_money

            if remaining_money <= 0:
                break
        print(
            f"{end_date_weekly.date()} open: ${week_open: .2f} close: ${week_close: .2f} strike: ${strike_price: .2f} stock: {stocks_count: .2f} rem_amount: ${remaining_money: .2f} Net Profit: ${profit:.2f} Deposited: ${deposit:.2f}")

        current_date += timedelta(weeks=1)
        end_date_weekly = min(current_date + timedelta(days=b_days - 1), end_date)


# Read stock prices from CSV file
def read_stock_prices_from_csv(file_path):
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    return df


# Example usage:
file_path = 'm.csv'
daily_stock_prices = read_stock_prices_from_csv(file_path)
x_percent = 100000  # Initial investment amount
a_percent = 103  # Strike price as a percentage of week open
b_days = 7  # Number of days in each week
start_date = datetime(2022, 12, 20)  # Change to your desired start date (closest Monday)
end_date = datetime(2023, 12, 18)  # Approximately 52 weeks from the start date

calculate_weekly_profit(daily_stock_prices, x_percent, a_percent, b_days, start_date, end_date)
