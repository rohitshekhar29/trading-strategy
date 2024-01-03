import pandas as pd

# Function to calculate the amount remaining
def calculate_remaining(investment, stock_quantity, stock_price, monthly_withdrawal, total_withdrawn):
    amount_withdrawn = total_withdrawn
    remaining_amount = (stock_quantity * stock_price) - amount_withdrawn - monthly_withdrawal
    remaining_amount_no_withdraw = stock_quantity * stock_price - amount_withdrawn
    return amount_withdrawn, remaining_amount, remaining_amount_no_withdraw

# Set variables
initial_investment = 500000
investment_date = '2014-01-01'
monthly_withdrawal = 4000
end_date = '2010-10-31'
factor = 1


# Read CSV files
csv_file_path = 'SnP.csv'  # Update with the actual path to your CSV file
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
stock_price_previous = initial_stock_price # Assuming the last business day of the previous month

# Initialize variables for gold
initial_gold_price = filtered_dfg['Close'].iloc[0]
total_gold = initial_investment * (1 - factor) / initial_gold_price  # Initial stock quantity bought on the investment date
initial_gold = total_gold
total_withdrawn_gold = 0
remaining_amount_gold = initial_investment * (1 - factor)
remaining_amount_gold_nowithdraw = initial_investment * (1 - factor)



# Create a list to store the results for tabular printing
results = []

# Process data for each month-end
for (_, group_df), (_, group_dfg) in zip(filtered_df.resample('M', on='Date'), filtered_dfg.resample('M', on='Date')):
    # Get the last business day of the month for both stock and gold data
    # Get the last business day of the month
    month_end_date = group_df['Date'].iloc[-1]

    # Extract stock price for the month-end date
    stock_price_current = group_df['Close'].iloc[-1]
    gold_price = group_dfg['Close'].iloc[-1]

    stock_price_change = (stock_price_current - stock_price_previous) / stock_price_previous
    if (stock_price_current * total_stock < (0.4 * initial_investment * factor) and remaining_amount_gold > 0.5 * initial_investment * (1 - factor)) or total_stock < 10:

        # Update total withdrawn from gold fund
        total_withdrawn_gold += monthly_withdrawal
        # Calculate the equivalent amount of gold ETFs to sell to fulfill the withdrawal
        gold_etfs_to_sell = monthly_withdrawal / gold_price
        total_gold -= gold_etfs_to_sell
        # Update remaining amount in gold fund
        remaining_amount_gold = total_gold * gold_price
        remaining_amount_gold_nowithdraw = initial_gold * gold_price
    else:
        stock_withdrawn = monthly_withdrawal / stock_price_current
        total_stock -= stock_withdrawn
        remaining_amount = total_stock * stock_price_current
        remaining_amount_no_withdraw = initial_stock * stock_price_current
        # Update total withdrawn
        total_withdrawn += monthly_withdrawal

    # Append results to the list
    results.append({
        'Month-End Date': month_end_date.strftime('%Y-%m-%d'),
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
print("\nResults:")
print("Initial Investment:", initial_investment)
print("Initial_price:", filtered_df['Close'].iloc[0])
print("Initial_stock:", initial_stock)
print("Final total stock:", remaining_amount)
print("Final total gold:", remaining_amount_gold)
print("Final total", remaining_amount_gold + remaining_amount)
print(results_df.to_string(index=False))


print("\nFinal Summary:")
print(final_summary_df.to_string(index=False))