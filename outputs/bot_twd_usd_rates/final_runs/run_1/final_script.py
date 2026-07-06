import asyncio
import sys
from pathlib import Path

from playwright.async_api import async_playwright

RUN_DIR = Path(__file__).parent
SCREENSHOTS = RUN_DIR / "screenshots"
SCREENSHOTS.mkdir(parents=True, exist_ok=True)
LOG = RUN_DIR / "final_script_log.txt"
LOG.write_text("", encoding="utf-8")

def log(step: int, msg: str) -> None:
    line = f"step {step} action: {msg}\n"
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(line, end="")

async def main():
    async with async_playwright() as playwright:
        browser = await playwright.firefox.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 1800})
        page = await context.new_page()

        # Step 1: Navigate to Bank of Taiwan exchange rate page
        await page.goto("https://rate.bot.com.tw/xrt?Lang=zh-TW", wait_until="domcontentloaded")
        await page.wait_for_selector("table", timeout=10000)
        await asyncio.sleep(1)
        await page.screenshot(path=str(SCREENSHOTS / "final_execution_1_navigate_page.png"))
        log(1, f"Navigate to 臺灣銀行牌告匯率 page. Title: {await page.title()}")

        # Step 2: Locate the USD row in the table
        usd_row = page.locator("table tbody tr").filter(has_text="USD")
        await page.screenshot(path=str(SCREENSHOTS / "final_execution_2_table_overview.png"))
        log(2, "Located USD row in the exchange rate table")

        # Step 3: Extract 現金買入 (Cash Buying) rate
        cash_buy_cell = usd_row.locator("td[data-table='本行現金買入']").first
        cash_buy_rate = await cash_buy_cell.inner_text()
        cash_buy_rate = cash_buy_rate.strip()
        await page.screenshot(path=str(SCREENSHOTS / "final_execution_3_usd_cash_buying.png"))
        log(3, f"USD 現金買入 (Cash Buying) rate: {cash_buy_rate}")

        # Step 4: Extract 現金賣出 (Cash Selling) rate
        cash_sell_cell = usd_row.locator("td[data-table='本行現金賣出']").first
        cash_sell_rate = await cash_sell_cell.inner_text()
        cash_sell_rate = cash_sell_rate.strip()
        await page.screenshot(path=str(SCREENSHOTS / "final_execution_4_usd_cash_selling.png"))
        log(4, f"USD 現金賣出 (Cash Selling) rate: {cash_sell_rate}")

        # Step 5: Record the final datum
        final_datum = f"美金 (USD) 現金買入匯率: {cash_buy_rate}, 現金賣出匯率: {cash_sell_rate}"
        with LOG.open("a", encoding="utf-8") as f:
            f.write(f"\nFINAL_RESPONSE: {final_datum}\n")
        log(5, f"Final datum recorded: {final_datum}")

        await browser.close()

asyncio.run(main())
