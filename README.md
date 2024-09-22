# CoinMarketCap Data Scraper

A Python script that scrapes cryptocurrency data from CoinMarketCap using Playwright and exports it to a CSV file.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Code Details](#code-details)
- [Output](#output)
- [Notes](#notes)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/iampukar/cmc-data-scraper.git
   cd cmc-data-scraper
   ```

2. **Install dependencies**:
  ```bash
  pip install -r requirements.txt
  ```

3. **Install Playwright browsers**:
  ```bash
  playwright install
  ```

## Usage
Run the script:
  ```bash
  python cmc-loader/cmc.py
  ```

This will:
- Open a headless browser.
- Navigate to the CoinMarketCap page.
- Click the "Load More" button multiple times.
- Scrape data and save it to a file `CMC_DATA.csv`.

## Code Details
- `click_load_more(page, max_clicks=9)`: Clicks the "Load More" button for `max_clicks` times to load additional rows.
- `fetch_rows_in_chunks(page, start_index, end_index, chunk_size=10)`: Fetches rows in chunks for better performance.
- `main()`: Orchestrates browser launch, scraping, and CSV export.

The data includes: `Rank, Name, Symbol, Link`

## Output
The data is saved in `CMC_DATA.csv` with the following columns:
`Rank, Name, Symbol, Link`

Example output:

  ```csv
  Rank,Name,Symbol,Link
  1,Bitcoin,BTC,https://coinmarketcap.com/currencies/bitcoin/
  2,Ethereum,ETH,https://coinmarketcap.com/currencies/ethereum/
  3,Tether,USDT,https://coinmarketcap.com/currencies/tether/
  ```

## Notes

- Adjust `max_clicks` in the `click_load_more` function if you need more or fewer rows.
- If experiencing timeouts, consider increasing wait times in `page.wait_for_timeout`.
