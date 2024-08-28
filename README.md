# Investment Screener Tool

## Overview

This project is a Python investment screening tool that scrapes financial data for companies listed on the S&P 500 and FTSE 100. The tool calculates various financial ratios and allows for filtering based on specific criteria to identify potential investment opportunities.

## Features

- **Data Scraping**: Retrieves ticker symbols from Wikipedia and financial data from Yahoo Finance.
- **Financial Ratios**: Calculates financial metrics such as PE Ratio, PB Ratio, ROE, Debt-to-Equity, Free Cash Flow and more.
- **Filtering**: Filters companies based on user-defined criteria to find the best investment opportunities.
- **Export**: Saves the filtered results and financial data to an Excel file.

## How to Use

1. Clone the repository:
    ```bash
    git clone https://github.com/camdens04/investment-screening-tool.git
    ```
2. Navigate to directory:
    ```bash
    cd investment_screening_tool
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Run script:
    ```bash
    python investment_screening_tool.py
    ```

## Dependencies

- `requests`
- `pandas`
- `beautifulsoup4`
- `yfinance`
- `openpyxl`

Install the dependencies using:
```bash
pip install -r requirements.txt
