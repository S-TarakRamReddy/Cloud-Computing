import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    reports_dir = os.path.dirname(__file__)
    html_file = f"file:///{os.path.join(reports_dir, 'mermaid_diagrams.html').replace(chr(92), '/')}"
    figures_dir = os.path.join(reports_dir, "figures")
    os.makedirs(figures_dir, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(html_file)
        await page.wait_for_timeout(3000) # wait for mermaid to render
        
        # Select locators and take screenshot
        arch = page.locator("#arch")
        await arch.screenshot(path=os.path.join(figures_dir, "arch.png"))
        
        ml = page.locator("#ml_pipeline")
        await ml.screenshot(path=os.path.join(figures_dir, "ml_pipeline.png"))
        
        wf = page.locator("#workflow")
        await wf.screenshot(path=os.path.join(figures_dir, "workflow.png"))
        
        cloud = page.locator("#cloud_arch")
        await cloud.screenshot(path=os.path.join(figures_dir, "cloud_arch.png"))
        
        await browser.close()
        print("Diagrams successfully generated.")

if __name__ == "__main__":
    asyncio.run(main())
