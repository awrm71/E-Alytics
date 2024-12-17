# E-Alytics: CS2 Demos Analysis  

Student Name:  Adam Murphy
Student Email:  admurphy@syr.edu

# E-Alytics: CS2 Demos Analysis  

### What it Does  

The **E-Alytics: CS2 Demos Analysis** is a comprehensive and interactive dashboard for analyzing **CS2 match and tournament data**. It combines pre-scraped tournament data with user-uploaded `.dem` files, which are parsed using [awpy](https://github.com/pnxenopoulos/awpy) and [demoparser2](https://github.com/akiver/demoparser2), to provide detailed statistics, game events, and visualizations. This tool simplifies the analysis of competitive CS2 matches for esports enthusiasts, players, and analysts.


#### **Tournament and Match Selection**  
At the top of the application, users can select a **specific tournament** and match from two pre-loaded datasets:  
- `tournaments.csv`: A list of tournaments scraped directly from HLTV, saving users from manually navigating the site.  
- `tournament_matches.csv`: A detailed file containing matchups, scores, and HLTV links for selected tournaments.  

For any selected match, the following information is displayed:  
- **Tournament Name**  
- **Matchup** between Team 1 and Team 2  
- **Final Score**  
- A direct **HLTV link** to view match details on the HLTV website  

This feature allows users to quickly locate match data and jump directly to the HLTV page for further exploration.  

#### **User-Uploaded Match Analysis**  
Users can upload **CS2 `.dem` files** (match demo files) for advanced analysis. The uploaded matches are processed to extract detailed player statistics and game event data, presented through two main views:  

### **Summary Stats**  
- Displays key player metrics such as kills, assists, deaths, rounds played, and ratings.  
- Supports dynamic filtering by **clan** and **team side** (CT or TERRORIST).  
- Combines statistics from multiple matches while avoiding duplication using automated data processing with **pandas**.  

### **Game Events Viewer**  
- Organized expandable sections display specific **game events** such as kills, damages, grenades, smokes, bomb plants/defuses, and infernos.  
- Each event type can be downloaded as a **CSV file** for offline analysis.  

> **Important Note**: When uploading multiple `.dem` files, ensure they belong to the **same series or match** to avoid errors caused by processing more than two teams at once.  

### **Visualizations and Heatmaps**  
The project dynamically generates **heatmaps** for kills and deaths using extracted player data. These heatmaps provide visual insights into **player activity**, positioning, and areas of engagement on the selected map. The data is parsed from `.dem` files using tools like **awpy** and **demoparser2**, and further automated manipulation is performed with **pandas** to streamline data formatting and aggregation.  

- **Customizable Maps**: Users can choose a specific map to compare head-to-head matchups, displaying details such as the attacker, victim, weapon used, damage dealt, and whether it was a headshot.  
- **Team Comparison**: Separate heatmaps for Team 1 and Team 2 illustrate tactical differences and hotspots for both kills and deaths, enabling users to identify patterns and strategies effectively.  

This feature helps users identify patterns, strategies, and gameplay trends efficiently.  

#### **File Handling and Notes**  
- **Downloading Files**: Users are instructed to download files via the **Download CSV** buttons on the right side of the page.  
- **Uploading Files**: After downloading `.dem` files, move them into the `cache` folder located in the project repository.  
- **Handling `.rar` Files**: If files are downloaded in `.rar` format, use [7-Zip](https://www.7-zip.org/) to unzip them. Simply install 7-Zip, right-click the file, and select "Extract Here."  

Additionally, sample `.dem` files for experimentation are provided in this **[OneDrive Folder](PLACEHOLDER_LINK)** so users can test the dashboard without needing to obtain their own files.  

---

### How you run my project

### How You Run My Project  

To run the **E-Alytics** project, follow these steps:  

1. **Set Up the Environment**:  
   - Clone this repository from GitHub.  
   - Install the required dependencies by running:  
     ```bash
     pip install -r requirements.txt
     ```  
This will start the Streamlit application in your default browser.
2. **File Directory Structure**:  
   Ensure the following file structure exists:  
   ```plaintext
   project-awrm71/
   ├── cache/
   │   ├── tournaments.csv          # Predefined tournaments list
   │   ├── tournament_matches.csv   # Matchups with scores and HLTV links
   │   └── other cached files
   ├── code/
   │   ├── Stats.py                 # Parsing functions
   │   ├── stat_viz.py              # Heatmap and stats visualizations
   │   ├── map_viz.py               # Map visualization logic
   │   └── E-Alytics.py             # Main Streamlit app
   │   └── match.py                 # HLTV tournament/match scraper
   └── about-project.md
   └── reflection.md
   └── requirements.txt

## Interact with the Application

#### Tournament and Match Selection
- Select a tournament and match from the sidebar to view the HLTV link, matchup, and final score.

#### Upload and Analyze
- Upload `.dem` files into the `cache` folder to analyze player stats, game events, and visualizations.

#### Summary Stats Viewer
- Filter player performance by teams and sides, summarizing key metrics.

#### Game Events Viewer
- Download datasets for kills, damages, grenades, and other game events.

#### Visualizations
- View detailed heatmaps showing kill and death activity on customizable maps.

## File Handling Notes

- **Uploading Files**: Move downloaded `.dem` files into the `cache` folder before uploading them in the app.
- **Handling `.rar` Files**: Use [7-Zip](https://www.7-zip.org/) to extract compressed `.rar` files if necessary.
- **Sample Files**: Sample `.dem` files are available in this **[OneDrive Folder](PLACEHOLDER_LINK)** for testing purposes.

By following these steps, users can seamlessly analyze CS2 match data, explore team strategies through visuals, and extract meaningful insights using this interactive dashboard.

### Other Important Notes

- **File Limitations**: Avoid running more than one `.dem` file with different teams competing, as this will cause issues in the application.
- **Processing Time**: Be patient while loading files. These files are large, and the package requires significant time to parse `.dem` files into usable data for the application.
- **File Dependencies**: Ensure the following files are executed in this order before running `E-Alytics.py`:
  1. `Stats.py`
  2. `map_viz.py`
  3. `stats_viz.py`
- **Experimental Files**: Files such as `E-test.py` and `parser.ipynb` are for experimentation and data manipulation testing. They are not required for running the application but can be explored for additional insights.
- **Temp files**: For some reason when parsing these files in Streamlit, duplicate .dem files will appear in the project folder with `temp_` at the start. I didn't have time to fix these issues once i realized they were happening so if this occurs just delete them as it wont hurt this application or the original files.