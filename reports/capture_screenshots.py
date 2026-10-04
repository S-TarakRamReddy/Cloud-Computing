import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    reports_dir = os.path.join(os.path.dirname(__file__), "screenshots")
    os.makedirs(reports_dir, exist_ok=True)
    
    BASE_URL = "https://cloud-computing.tarakram.blitz.cloud"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 900})
        
        print("Capturing Dashboard...")
        await page.goto(f"{BASE_URL}/index.html")
        await page.wait_for_timeout(3000)
        await page.screenshot(path=os.path.join(reports_dir, "01_dashboard.png"))
        
        print("Capturing Swagger API...")
        await page.goto(f"{BASE_URL}/docs")
        await page.wait_for_timeout(3000)
        await page.screenshot(path=os.path.join(reports_dir, "07_swagger.png"))

        print("Capturing Legitimate Prediction...")
        await page.goto(f"{BASE_URL}/index.html")
        await page.wait_for_timeout(2000)
        await page.click("button:has-text('Select Legitimate Example')")
        await page.wait_for_timeout(2000)
        await page.screenshot(path=os.path.join(reports_dir, "02_legitimate_demo.png"))
        await page.click("button:has-text('Predict Fraud Risk')")
        await page.wait_for_timeout(3000)
        await page.screenshot(path=os.path.join(reports_dir, "03_legitimate_prediction.png"))

        print("Capturing Fraud Prediction...")
        await page.reload()
        await page.wait_for_timeout(2000)
        await page.click("button:has-text('Select Fraud Example')")
        await page.wait_for_timeout(2000)
        await page.screenshot(path=os.path.join(reports_dir, "04_fraud_demo.png"))
        await page.click("button:has-text('Predict Fraud Risk')")
        await page.wait_for_timeout(3000)
        await page.screenshot(path=os.path.join(reports_dir, "05_fraud_prediction.png"))
        
        print("Capturing Transaction History & Statistics...")
        await page.reload()
        await page.wait_for_timeout(3000)
        await page.screenshot(path=os.path.join(reports_dir, "06_transaction_history.png"))
        
        await browser.close()
        print("Screenshots captured successfully from Blitz Cloud.")

if __name__ == "__main__":
    asyncio.run(main())
