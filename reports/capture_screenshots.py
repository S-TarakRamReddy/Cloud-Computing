import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    reports_dir = os.path.join(os.path.dirname(__file__), "screenshots")
    os.makedirs(reports_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        
        # 1. Homepage/Dashboard
        await page.goto("http://localhost:8080/")
        await page.wait_for_timeout(2000) # wait for stats to load
        await page.screenshot(path=os.path.join(reports_dir, "01_dashboard.png"))
        
        # 2. Swagger API
        await page.goto("http://localhost:8000/docs")
        await page.wait_for_timeout(2000)
        await page.screenshot(path=os.path.join(reports_dir, "07_swagger.png"))

        # 3. Legitimate Prediction
        await page.goto("http://localhost:8080/")
        await page.click("button:has-text('Select Legitimate Example')")
        await page.wait_for_timeout(3000)
        await page.click("button:has-text('Predict Fraud Risk')")
        await page.wait_for_timeout(3000)
        await page.screenshot(path=os.path.join(reports_dir, "03_legitimate_prediction.png"))

        # 4. Fraud Prediction
        await page.click("button:has-text('Select Fraud Example')")
        await page.wait_for_timeout(3000)
        await page.click("button:has-text('Predict Fraud Risk')")
        await page.wait_for_timeout(3000)
        await page.screenshot(path=os.path.join(reports_dir, "04_fraud_prediction.png"))
        
        # 5. Transaction History (refresh to see both)
        await page.reload()
        await page.wait_for_timeout(1000)
        await page.screenshot(path=os.path.join(reports_dir, "05_transaction_history.png"))
        
        await browser.close()
        print("Screenshots captured successfully.")

if __name__ == "__main__":
    asyncio.run(main())
