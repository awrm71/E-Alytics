import os
import json
import time
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

# Load cookies from file
# Load cookies from file
# Load cookies from file and validate
def load_cookies(context, cookies_path="cookies.json"):
    if os.path.exists(cookies_path):
        with open(cookies_path, "r") as f:
            cookies = json.load(f)
            
            # Ensure cookies are in a list
            if isinstance(cookies, dict):
                cookies = [cookies]
            
            # Validate cookies to ensure required keys are present
            valid_cookies = []
            for cookie in cookies:
                if "name" in cookie and "value" in cookie and "domain" in cookie:
                    valid_cookies.append(cookie)
                else:
                    print(f"Skipping invalid cookie: {cookie}")
            
            if valid_cookies:
                context.add_cookies(valid_cookies)
                print("Cookies loaded successfully.")
            else:
                print("No valid cookies found to load.")
    else:
        print("No cookies file found. Proceeding without cookies.")



# Save cookies after successful verification
def save_cookies(context, cookies_path="cookies.json"):
    cookies = context.cookies()
    with open(cookies_path, "w") as f:
        json.dump(cookies, f)
    print("Cookies saved successfully for future use.")

# Main scraping function
def bypass_cloudflare_and_download():
    with sync_playwright() as p:
        print("Launching browser...")
        # Launch the browser
        browser = p.chromium.launch(headless=False)  # Run in visible mode
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            locale="en-US",
            viewport={"width": 1920, "height": 1080},
            proxy={"server": "http://your-proxy-ip:port"} if os.getenv("USE_PROXY") else None
        )

        # Load cookies if available
        load_cookies(context)

        # Create a new page
        page = context.new_page()

        # Apply stealth mode
        stealth_sync(page)

        # Target download URL
        demo_link = "https://www.hltv.org/matches/2375428/eternal-fire-vs-natus-vincere-esl-pro-league-season-20"
        print("Navigating to download link...")
        page.goto(demo_link, wait_until="networkidle")

        # Verify manual interaction
        if "verify" in page.url.lower():
            print("Manual verification required. Complete it in the browser...")
            input("Press ENTER after completing the verification...")
            save_cookies(context)  # Save cookies after solving the verification

        # Check if the page redirects to download
        if "download" in page.url:
            print(f"File download triggered successfully. URL: {page.url}")
        else:
            print("Verification or download failed. Try manual interaction again.")

        # Keep the browser open for inspection
        input("Press ENTER to close the browser...")
        browser.close()

if __name__ == "__main__":
    bypass_cloudflare_and_download()
