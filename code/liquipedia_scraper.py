import pandas as pd
from playwright.sync_api import sync_playwright

def scrape_liquipedia_results(tournament_url: str):
    """
    Scrape match results from a Liquipedia CS2 tournament page.

    Args:
        tournament_url (str): URL of the Liquipedia CS2 tournament page.

    Returns:
        pd.DataFrame: A DataFrame containing team names, scores, maps, and match dates.
    """
    # Placeholder for scraped data
    match_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Go to the tournament page
        print("Navigating to the tournament page...")
        page.goto(tournament_url)
        page.wait_for_selector(".match-row", timeout=10000)  # Wait for matches to load

        # Extract match data
        matches = page.query_selector_all(".match-row")
        for match in matches:
            try:
                team1 = match.query_selector(".team-left").inner_text()
                team2 = match.query_selector(".team-right").inner_text()
                score = match.query_selector(".match-result").inner_text()
                map_name = match.query_selector(".match-map").inner_text()
                date = match.query_selector(".match-date").inner_text()

                match_data.append({
                    "Team 1": team1.strip(),
                    "Team 2": team2.strip(),
                    "Score": score.strip(),
                    "Map": map_name.strip(),
                    "Date": date.strip()
                })
            except Exception as e:
                print(f"Error parsing match: {e}")
                continue

        browser.close()

    # Return match data as DataFrame
    return pd.DataFrame(match_data)
