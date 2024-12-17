import csv
import os
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# Input and Output File Paths
input_csv = os.path.abspath(os.path.join("cache", "tournaments.csv"))
output_csv = os.path.abspath(os.path.join("cache", "tournament_matches.csv"))

# Async function to scrape match details
async def scrape_tournament_matches(tournament_name, event_id):
    matches = []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # Keep browser visible for debugging
            page = await browser.new_page()

            # Construct the results page URL
            results_url = f"https://www.hltv.org/results?event={event_id}"
            print(f"Accessing: {results_url}")
            await page.goto(results_url)

            # Handle cookie consent
            try:
                await page.get_by_role("button", name="Allow all cookies").click()
                print("Cookies allowed.")
            except Exception:
                print("No cookie banner found.")

            await asyncio.sleep(3)  # Wait for the page to load fully

            # Extract page content and parse with BeautifulSoup
            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")

            # Find all match entries
            match_entries = soup.find_all("div", class_="result-con")
            for match in match_entries:
                # Match Link
                match_link_tag = match.find("a", class_="a-reset")
                match_url = "https://www.hltv.org" + match_link_tag["href"] if match_link_tag else "N/A"

                # Team Names
                team_cells = match.find_all("div", class_="line-align")
                team1 = team_cells[0].text.strip() if len(team_cells) > 0 else "N/A"
                team2 = team_cells[1].text.strip() if len(team_cells) > 1 else "N/A"

                # Match Score
                score_tag = match.find("td", class_="result-score")
                if score_tag:
                    score_won = score_tag.find("span", class_="score-won").text.strip() if score_tag.find("span", class_="score-won") else "0"
                    score_lost = score_tag.find("span", class_="score-lost").text.strip() if score_tag.find("span", class_="score-lost") else "0"
                    score = f"{score_won} - {score_lost}"
                else:
                    score = "N/A"

                # Append match data
                matches.append({
                    "Tournament": tournament_name,
                    "Match Link": match_url,
                    "Team 1": team1,
                    "Team 2": team2,
                    "Score": score
                })

            await browser.close()
    except Exception as e:
        print(f"Error scraping {tournament_name}: {e}")
    return matches

# Main Async Function
async def main():
    if not os.path.exists(input_csv):
        print(f"Error: Input file not found at {input_csv}. Exiting...")
        return

    # Read tournament data
    tournaments = []
    with open(input_csv, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Extract event_id from the tournament link
            event_id = row["Link"].split('/')[-2]
            tournaments.append({"name": row["Event Name"], "event_id": event_id})

    # Scrape matches for each tournament
    all_matches = []
    for tournament in tournaments:
        print(f"Scraping matches for {tournament['name']}...")
        tournament_matches = await scrape_tournament_matches(tournament["name"], tournament["event_id"])
        all_matches.extend(tournament_matches)

    # Save match data to CSV
    output_fields = ["Tournament", "Match Link", "Team 1", "Team 2", "Score"]
    with open(output_csv, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=output_fields)
        writer.writeheader()
        for match in all_matches:
            writer.writerow(match)

    print(f"Scraping complete. Match data saved to: {output_csv}")

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
