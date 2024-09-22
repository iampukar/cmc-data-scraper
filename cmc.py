import logging
import pandas as pd
from playwright.async_api import async_playwright
import asyncio

# Set up logging for verbose display
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def click_load_more(page, max_clicks=9):
    clicks = 0
    while clicks < max_clicks:
        logger.info(f"Clicking 'Load More' button (Click {clicks + 1})...")
        load_more_button = await page.query_selector("div.cmc-table-listing__loadmore > button[type='button']")
        if load_more_button:
            await load_more_button.click()
            await page.wait_for_timeout(3000)  # Wait a bit longer for new rows to load
            clicks += 1
        else:
            logger.info("'Load More' button not found or no more rows to load.")
            break
    logger.info(f"Total 'Load More' button clicks: {clicks}")
    return clicks

async def fetch_rows_in_chunks(page, start_index, end_index, chunk_size=10):
    data = []
    for i in range(start_index, end_index, chunk_size):
        await page.evaluate(f"window.scrollTo(0, document.querySelectorAll('tr.cmc-table-row')[{i}].offsetTop)")
        await page.wait_for_timeout(3000)
        
        for j in range(i, min(i + chunk_size, end_index)):
            row_selector = f"tr.cmc-table-row:nth-child({j + 1})"
            row = await page.query_selector(row_selector)
            if row:
                logger.debug(f"Processing row {j + 1}...")
                
                rank_div = await row.query_selector("td:nth-child(1) div")
                rank = await rank_div.inner_text() if rank_div else None
                logger.debug(f"Rank: {rank}")
                
                name_symbol_div = await row.query_selector("td:nth-child(2) div")
                
                if name_symbol_div:
                    name_element = await name_symbol_div.query_selector("a.cmc-table__column-name--name")
                    name = await name_element.inner_text() if name_element else None
                    logger.debug(f"Name: {name}")
                    
                    link = await name_element.get_attribute("href") if name_element else None
                    logger.debug(f"Link: {link}")
                else:
                    name = None
                    link = None
                    logger.warning(f"Could not find name_symbol_div for row {j + 1}")

                symbol_div = await row.query_selector("td:nth-child(3) div")
                symbol = await symbol_div.inner_text() if symbol_div else None
                logger.debug(f"Symbol: {symbol}")
                
                data.append({
                    "Rank": rank,
                    "Name": name,
                    "Symbol": symbol,
                    "Link": f"https://coinmarketcap.com{link}" if link else None
                })
            else:
                logger.warning(f"Could not find row {j + 1}")
    
    return data

async def main():
    async with async_playwright() as p:
        # Launch the browser in headless mode
        logger.info("Launching the browser...")
        browser = await p.chromium.launch(headless=True)

        # Create a new browser context with a user-agent
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = await context.new_page()

        url = "https://coinmarketcap.com/all/views/all/"
        logger.info(f"Navigating to {url}...")
        response = await page.goto(url)
        
        if response and response.status == 200:
            logger.info(f"Response received with status code: {response.status}")
        else:
            logger.error(f"Failed to load the page. Status code: {response.status if response else 'No response'}")
            await browser.close()
            return

        # Click "Load More" button multiple times until reaching the rows count
        max_clicks = 9  # 200 rows are loaded per click, so adjust this number based on your requirements
        await click_load_more(page, max_clicks=max_clicks)

        total_rows = len(await page.query_selector_all("tr.cmc-table-row"))
        logger.info(f"Total number of rows found: {total_rows}")

        all_data = await fetch_rows_in_chunks(page, 0, total_rows, chunk_size=10)

        df = pd.DataFrame(all_data)
        df.set_index('Rank', inplace=True)

        csv_filename = "CMC_DATA.csv"
        df.to_csv(csv_filename)
        logger.info(f"Data saved to {csv_filename}")

        logger.info("Closing the browser...")
        await browser.close()

if __name__ == "__main__":
    logger.info("Starting the script...")
    asyncio.run(main())
