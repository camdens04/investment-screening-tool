import requests
import pandas as pd
from bs4 import BeautifulSoup
import yfinance as yf
import os
from datetime import datetime

# Function to scrape ticker symbols from Wikipedia for S&P 500
def get_sp500_tickers():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    table = soup.find('table', {'id': 'constituents'})
    tickers = [row.find_all('td')[0].text.strip() for row in table.find_all('tr')[1:]]
    return tickers

# Function to scrape ticker symbols from FTSE 100
def get_ftse100_tickers():
    url = 'https://en.wikipedia.org/wiki/FTSE_100_Index'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    table = soup.find_all('table', {'class': 'wikitable sortable'})[1]
    tickers = []
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        if len(cols) > 1:
            ticker = cols[1].text.strip()
            tickers.append(ticker + '.L')  # Adding '.L' for LSE tickers
    return tickers

# Validate ticker symbols
def validate_tickers(tickers):
    valid_tickers = []
    for ticker in tickers:
        if ticker.isalnum() or ('.L' in ticker and ticker.replace('.L', '').isalnum()):
            valid_tickers.append(ticker)
    return valid_tickers

# Function to fetch financial data using Yahoo Finance
def get_financial_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Safely handle missing data by using .get() method with a default value of None
        return {
            'Ticker': ticker,
            'PE_Ratio': info.get('forwardPE', None),
            'PB_Ratio': info.get('priceToBook', None),
            'ROE': info.get('returnOnEquity', None),
            'Debt_to_Equity': info.get('debtToEquity', None),
            'Free_Cash_Flow': info.get('freeCashflow', None),
            'ROIC': info.get('returnOnAssets', None),  # ROIC might not be directly available
            'PS_Ratio': info.get('priceToSalesTrailing12Months', None),
            'Enterprise_Value': info.get('enterpriseValue', None),
            'EV_to_EBITDA': info.get('enterpriseToEbitda', None),
            'Dividend_Yield': info.get('dividendYield', None)
        }
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

# Calculating financial ratios
def calculate_ratios(sp500_tickers, ftse100_tickers):
    ratios = []

    for ticker in sp500_tickers:
        data = get_financial_data(ticker)
        if data:
            ratios.append(data)

    for ticker in ftse100_tickers:
        data = get_financial_data(ticker)
        if data:
            ratios.append(data)

    return pd.DataFrame(ratios)

# Broadened filtering function with additional criteria
def filter_companies(df, pe_ratio_range=(5, 30), pb_ratio_range=(0.5, 5), roe_min=0.05,
                     debt_to_equity_max=1.0, free_cash_flow_min=0, ps_ratio_max=3, ev_to_ebitda_max=15,
                     roic_min=0.05, dividend_yield_min=None):
    filtered_df = df.copy()

    if pe_ratio_range:
        filtered_df = filtered_df[filtered_df['PE_Ratio'].between(pe_ratio_range[0], pe_ratio_range[1], inclusive='both')]
    if pb_ratio_range:
        filtered_df = filtered_df[filtered_df['PB_Ratio'].between(pb_ratio_range[0], pb_ratio_range[1], inclusive='both')]
    if roe_min:
        filtered_df = filtered_df[filtered_df['ROE'] >= roe_min]
    if debt_to_equity_max:
        filtered_df = filtered_df[filtered_df['Debt_to_Equity'] <= debt_to_equity_max]
    if free_cash_flow_min:
        filtered_df = filtered_df[filtered_df['Free_Cash_Flow'] >= free_cash_flow_min]
    if ps_ratio_max:
        filtered_df = filtered_df[filtered_df['PS_Ratio'] <= ps_ratio_max]
    if ev_to_ebitda_max:
        filtered_df = filtered_df[filtered_df['EV_to_EBITDA'] <= ev_to_ebitda_max]
    if roic_min:
        filtered_df = filtered_df[filtered_df['ROIC'] >= roic_min]

    if dividend_yield_min is not None:
        filtered_df = filtered_df[filtered_df['Dividend_Yield'] >= dividend_yield_min]

    return filtered_df

# Function to save the filtered companies to an Excel file with multiple sheets
def save_to_excel(filtered_df, ratios, filename="daily_report.xlsx"):
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        ratios[ratios['Ticker'].isin(sp500_tickers)].to_excel(writer, sheet_name='S&P 500', index=False)
        ratios[ratios['Ticker'].isin(ftse100_tickers)].to_excel(writer, sheet_name='FTSE 100', index=False)
        filtered_df.to_excel(writer, sheet_name='Filtered', index=False)

# Create the output directory if it doesn't exist
output_dir = 'daily_reports'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Get ticker lists
sp500_tickers = get_sp500_tickers()
ftse100_tickers = get_ftse100_tickers()

# Validate tickers
sp500_tickers = validate_tickers(sp500_tickers)
ftse100_tickers = validate_tickers(ftse100_tickers)

# Print number of tickers fetched and first few tickers for verification
print(f"S&P 500 Tickers ({len(sp500_tickers)}): {sp500_tickers[:5]} ...")
print(f"FTSE 100 Tickers ({len(ftse100_tickers)}): {ftse100_tickers[:5]} ...")

# Calculate financial ratios
ratios = calculate_ratios(sp500_tickers, ftse100_tickers)

# Print number of tickers processed and first few tickers for verification
print(f"Total Tickers Processed: {len(ratios)}")
print(ratios.head())

# Example of filtering companies with broadened criteria
filtered_companies = filter_companies(
    ratios,
    pe_ratio_range=(5, 35),
    pb_ratio_range=(0.5, 10),
    roe_min=0.02,
    debt_to_equity_max=2.0,
    free_cash_flow_min=0,
    ps_ratio_max=6,
    ev_to_ebitda_max=25,
    roic_min=0.02,
    dividend_yield_min=0.01  # Broadened to include companies with even small dividends
)

# Display filtered companies
print("Filtered Companies based on broadened criteria:")
print(filtered_companies)

# Save the filtered companies and ratios to an Excel file
today_date = datetime.now().strftime('%Y-%m-%d')
filename = f"{output_dir}/investment_screening_{today_date}.xlsx"
save_to_excel(filtered_companies, ratios, filename)

print(f"Filtered companies saved to {filename}")
