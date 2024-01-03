import pandas as pd


# Function to calculate the amount remaining
def calculate_remaining(investment, stock_quantity, stock_price, monthly_withdrawal, total_withdrawn):
    amount_withdrawn = total_withdrawn
    remaining_amount = (stock_quantity * stock_price) - amount_withdrawn - monthly_withdrawal
    remaining_amount_no_withdraw = stock_quantity * stock_price - amount_withdrawn
    return amount_withdrawn, remaining_amount, remaining_amount_no_withdraw


# Set variables
initial_investment = 500000
investment_date = '2005-01-15'
monthly_withdrawal = 5000
end_date = '2023-10-31'
factor = 1
ratio = 1

# Read CSV files
csv_file_path = 'SP.csv'  # Update with the actual path to your CSV file
gold_file_path = 'iau.csv'
df = pd.read_csv(csv_file_path)
dfg = pd.read_csv(gold_file_path)

# Convert 'Date' column to datetime
df['Date'] = pd.to_datetime(df['Date'])
dfg['Date'] = pd.to_datetime(dfg['Date'])

# Filter data based on the investment date
filtered_df = df[(df['Date'] >= pd.to_datetime(investment_date)) & (df['Date'] <= pd.to_datetime(end_date))]
filtered_dfg = dfg[(dfg['Date'] >= pd.to_datetime(investment_date)) & (dfg['Date'] <= pd.to_datetime(end_date))]

# Initialize variables
initial_stock_price = filtered_df['Close'].iloc[0]
total_stock = initial_investment * factor / initial_stock_price  # Initial stock quantity bought on the investment date
initial_stock = total_stock
total_withdrawn = 0
remaining_amount = initial_investment * factor
remaining_amount_no_withdraw = remaining_amount
stock_price_previous = initial_stock_price  # Assuming the last business day of the previous month

# Initialize variables for gold
initial_gold_price = filtered_dfg['Close'].iloc[0]
total_gold = initial_investment * (
        1 - factor) / initial_gold_price  # Initial stock quantity bought on the investment date
initial_gold = total_gold
total_withdrawn_gold = 0
remaining_amount_gold = initial_investment * (1 - factor)
remaining_amount_gold_nowithdraw = initial_investment * (1 - factor)

# Create a list to store the results for tabular printing
results = []
total = 0
missed = 0
distribution = {1: ratio, 0.5: ratio - 0.1, 0.25: ratio - 0.2, 0.125: ratio - 0.3}

# Process data for each month-end
for (_, group_df), (_, group_dfg) in zip(filtered_df.resample('M', on='Date'), filtered_dfg.resample('M', on='Date')):
    # Modify the code where withdrawal amount is calculated
    # Replace the fixed monthly_withdrawal with a dynamic withdrawal percentage
    # Calculate the withdrawal percentage based on portfolio value ranges


    total += 1
    month_end_date = group_df['Date'].iloc[-1]

    # Extract stock price for the month-end date
    stock_price_current = group_df['Close'].iloc[-1]
    gold_price = group_dfg['Close'].iloc[-1]
    remaining_amount_gold = gold_price * total_gold
    remaining_amount = total_stock * stock_price_current

    withdrawal_percentage = 0
    gold = remaining_amount_gold
    stock = remaining_amount
    if gold + stock < 0.8 * initial_investment:
        withdrawal_percentage = 0.01
    elif 0.8 * initial_investment < gold + stock < 0.9 * initial_investment:
        withdrawal_percentage = 0.01
    elif 0.9 * initial_investment < gold + stock <= 1 * initial_investment:
        withdrawal_percentage = 0.01
    elif 1.0 * initial_investment < gold + stock <= 1.25 * initial_investment:
        withdrawal_percentage = 0.02
    elif 1.25 * initial_investment < gold + stock <= 1.5 * initial_investment:
        withdrawal_percentage = 0.03
    elif 1.5 * initial_investment < gold + stock + remaining_amount:
        withdrawal_percentage = 0.05
    wd = (gold + stock) * withdrawal_percentage

    # Get the last business day of the month for both stock and gold data
    # Get the last business day of the month

    stock_price_change = (stock_price_current - stock_price_previous) / stock_price_previous
    # fraction = distribution[wd / monthly_withdrawal]
    condition1 = (stock_price_current * total_stock) <= ((factor) * initial_investment)
    condition2 = remaining_amount_gold * gold_price > 0.1 * initial_gold * initial_gold_price

    if (condition1 and condition2):
        # Update total withdrawn from gold fund
        gold_withdrawn = wd / gold_price
        total_gold -= gold_withdrawn
        remaining_amount_gold = total_gold * gold_price
        remaining_amount_gold_nowithdraw = initial_gold * gold_price
        # Update total withdrawn
        total_withdrawn_gold += wd
    else:
        stock_withdrawn = wd / stock_price_current
        total_stock -= stock_withdrawn
        remaining_amount = total_stock * stock_price_current
        remaining_amount_no_withdraw = initial_stock * stock_price_current
        # Update total withdrawn
        total_withdrawn += wd
    # Append results to the list
    results.append({
        'Month-End Date': month_end_date.strftime('%Y-%m-%d'),
        'Withdraw': f"${wd: .2f}",
        'Withdrawn': f"${total_withdrawn:.2f}",
        'StockRemaining': f"{total_stock:.2f} units",
        'StockPrice': f"${stock_price_current:.2f}",
        'AmountRemaining': f"${total_stock * stock_price_current:.2f}",
        'AmountRemaining(NW)': f"${stock_price_current * initial_stock:.2f}",
        'AmountWithdrawnGold': f"${total_withdrawn_gold:.2f}",
        'GoldQuantityRemaining': f"{total_gold:.2f} units",
        'CurrentGoldPrice': f"${gold_price:.2f}",
        'GoldAmountRemaining': f"${gold_price * total_gold:.2f}",
        'GoldAmountRemaining(NW)': f"${initial_gold * gold_price:.2f}"
    })
    stock_price_previous = stock_price_current  # Assuming the last business day of the previous month

# Final summary
final_summary = {
    'Total Amount Withdrawn': f"${total_withdrawn:.2f}",
    'Final Stock Quantity Remaining': f"{total_stock:.2f} units",
    'Final Amount Remaining': f"${remaining_amount:.2f}",
    'Final Amount Remaining (No Withdraw)': f"${remaining_amount_no_withdraw:.2f}",
    'Total Amount Withdrawn Gold ': f"${total_withdrawn_gold:.2f}",
    'Final gold Quantity Remaining': f"{total_gold:.2f} units",
    'Final Amount Remaining': f"${remaining_amount_gold:.2f}",
    'Final Amount Remaining (No Withdraw)': f"${remaining_amount_gold_nowithdraw:.2f}",
}

# Convert the results and final summary to DataFrames for tabular printing
results_df = pd.DataFrame(results)
final_summary_df = pd.DataFrame([final_summary])

# Print the results in tabular form

print("\nFinal Summary:")
print(final_summary_df.to_string(index=False))

print(results_df.to_string(index=False))

print("\nResults:")
print("Initial Investment:", initial_investment)
print("Initial_price:", filtered_df['Close'].iloc[0])
print("Initial_stock:", initial_stock)
print("Final total stock:", remaining_amount)
print("Final total gold:", remaining_amount_gold)
print("Final total remaining", remaining_amount_gold + remaining_amount)
print("Final total including withdrawl",
      remaining_amount_gold + remaining_amount + total_withdrawn + total_withdrawn_gold)
print("Total Withdrawn", (total_withdrawn + total_withdrawn_gold))
print(missed, total, (total_withdrawn + total_withdrawn_gold) / total)
