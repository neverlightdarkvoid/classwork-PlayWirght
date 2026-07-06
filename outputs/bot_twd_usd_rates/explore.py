import asyncio
import sys
from pathlib import Path

from playwright.async_api import async_playwright

WORKSPACE = Path(r"C:\Users\ASUS\Documents\GitHub\classwork-PlayWirght\outputs\bot_twd_usd_rates")
SCREENSHOTS = WORKSPACE / "screenshots"
SCREENSHOTS.mkdir(parents=True, exist_ok=True)

async def main():
    async with async_playwright() as playwright:
        browser = await playwright.firefox.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 1800})
        page = await context.new_page()

        await page.goto("https://rate.bot.com.tw/xrt?Lang=zh-TW", wait_until="domcontentloaded")
        await page.screenshot(path=str(SCREENSHOTS / "explore_1_start.png"))

        print("URL:", page.url)
        print("TITLE:", await page.title())

        # Wait for the table to load
        await page.wait_for_selector("table", timeout=10000)
        await asyncio.sleep(1)

        # Inspect the full page ARIA snapshot
        snapshot = await page.locator("body").aria_snapshot()
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        print("ARIA:", snapshot[:5000])

        # Also grab the table HTML for the USD row
        print("\n\n=== TABLE HTML (USD row) ===")
        rows = await page.locator("table tbody tr").all()
        for row in rows:
            text = await row.inner_text()
            if "USD" in text or "美金" in text or "美元" in text:
                html = await row.inner_html()
                print(f"Row text: {text}")
                print(f"Row HTML: {html}")
                break

        await browser.close()

asyncio.run(main())
