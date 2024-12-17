# import streamlit as st
# from demoparser2 import DemoParser
# import pandas as pd
# import time  # For simulating progress updates

# # Streamlit app title
# st.title("CS2 Demo File Parser with Progress Bars and Toggle Views")

# # File uploader
# uploaded_file = st.file_uploader("Upload a CS2 Demo File", type=["dem"])

# if uploaded_file:
#     try:
#         # Save the uploaded file to a temporary location
#         temp_file_path = "temp.dem"
#         with open(temp_file_path, "wb") as f:
#             f.write(uploaded_file.read())

#         # Show progress bar for parsing
#         st.info("Demo file uploaded successfully!")
#         st.write("Starting to parse the demo file...")

#         # Initialize progress bar
#         parse_progress = st.progress(0)

#         # Step 1: Initialize parser
#         parse_progress.progress(25)  # Update to 25%
#         parser = DemoParser(temp_file_path)
#         time.sleep(1)  # Simulate delay

#         # Step 2: Parse player_death events
#         st.write("Parsing events: `player_death`...")
#         event_df = parser.parse_event("player_death", player=["X", "Y"], other=["total_rounds_played"])
#         parse_progress.progress(50)  # Update to 50%

#         # Step 3: Parse ticks
#         st.write("Parsing ticks...")
#         ticks_df = parser.parse_ticks(["X", "Y"])
#         parse_progress.progress(75)  # Update to 75%

#         # Step 4: Finalize parsing
#         parse_progress.progress(100)  # Update to 100%
#         st.success("Demo parsing completed successfully!")

#         # Provide a toggle to view either DataFrame
#         st.subheader("Select DataFrame to View:")
#         selected_df = st.selectbox(
#             "Choose a DataFrame to display:",
#             options=["Player Death Events", "Ticks Data"],
#         )

#         # Display the selected DataFrame
#         if selected_df == "Player Death Events":
#             st.write("**Player Death Events DataFrame:**")
#             st.dataframe(event_df)
#         elif selected_df == "Ticks Data":
#             st.write("**Ticks DataFrame:**")
#             st.dataframe(ticks_df)

#         # Provide download options
#         st.subheader("Download DataFrames:")
#         st.download_button(
#             label="Download Events DataFrame as CSV",
#             data=event_df.to_csv(index=False),
#             file_name="player_death_events.csv",
#             mime="text/csv",
#         )
#         st.download_button(
#             label="Download Ticks DataFrame as CSV",
#             data=ticks_df.to_csv(index=False),
#             file_name="ticks_data.csv",
#             mime="text/csv",
#         )

#     except Exception as e:
#         st.error(f"An error occurred while parsing the file: {e}")
# else:
#     st.info("Please upload a .dem file to proceed.")


import streamlit as st
import pandas as pd
from awpy import Demo
from awpy.stats import kast
import time

def get_kast_data(demo_path, progress_callback):
    """
    Extract KAST data from a demo file using awpy, including team names.

    Parameters:
        demo_path (str): Path to the demo file.
        progress_callback (function): Function to update progress.

    Returns:
        pd.DataFrame: DataFrame containing player KAST statistics with team names.
    """
    # Initialize progress
    progress_callback(0.1)
    time.sleep(1)  # Simulating initial delay

    # Parse the demo
    demo = Demo(demo_path)
    progress_callback(0.3)

    # Parse the full demo to retrieve metadata, including team information
    parsed_data = demo.parse(return_type="json")
    progress_callback(0.5)

    # Extract team names and player associations
    try:
        team1_name = parsed_data["match"]["teamOne"]["name"]
        team2_name = parsed_data["match"]["teamTwo"]["name"]

        # Build a mapping of player SteamIDs to team names
        player_teams = {}
        for player in parsed_data["match"]["teamOne"]["players"]:
            player_teams[player["steamID"]] = team1_name
        for player in parsed_data["match"]["teamTwo"]["players"]:
            player_teams[player["steamID"]] = team2_name
    except KeyError as e:
        raise ValueError(f"Missing team or player data in the demo file: {e}")

    # Calculate KAST statistics
    kast_stats = kast(demo)
    progress_callback(0.8)

    # Convert to DataFrame
    kast_df = pd.DataFrame(kast_stats)

    # Add team names to the DataFrame
    kast_df["team_name"] = kast_df["steamid"].map(player_teams)
    progress_callback(1.0)

    kast_df = kast_df.rename(columns={"playerName": "name", "side": "side", "kast": "kast"})
    return kast_df

def filter_kast(df, team_name=None, side=None):
    """
    Filters KAST statistics by team and/or side.

    Parameters:
        df (pd.DataFrame): The DataFrame containing KAST statistics.
        team_name (str or None): The team to filter by (e.g., 'G2', 'Heroic'). Pass None to include all teams.
        side (str or None): The side to filter by ('CT', 'TERRORIST', or None for both).

    Returns:
        pd.DataFrame: Filtered DataFrame with columns: player_name, team_name, and KAST.
    """
    filtered_df = df.copy()

    # Filter by team_name if specified
    if team_name is not None and team_name != "All Teams":
        filtered_df = filtered_df[filtered_df['team_name'] == team_name]

    # Filter by side if specified
    if side is not None and side != "Both":
        filtered_df = filtered_df[filtered_df['side'] == side]

    # Select relevant columns
    filtered_df = filtered_df[['name', 'team_name', 'kast']]

    return filtered_df

# Streamlit App
def main():
    st.title("KAST Statistics Viewer")

    # File uploader
    uploaded_file = st.sidebar.file_uploader("Upload a demo file", type=["dem"])

    if uploaded_file is not None:
        try:
            # Save uploaded file to a temporary path
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.read())

            # Progress bar
            progress_bar = st.sidebar.progress(0)

            # Process the uploaded file with progress callback
            @st.cache_data(show_spinner=False)
            def process_demo_file(demo_path):
                return get_kast_data(demo_path, progress_callback=progress_bar.progress)

            df = process_demo_file(temp_path)

            # Sidebar filters
            team_names = ["All Teams"] + sorted(df["team_name"].unique().tolist())
            selected_team = st.sidebar.selectbox("Select Team", team_names)

            sides = ["Both", "CT", "TERRORIST"]
            selected_side = st.sidebar.selectbox("Select Side", sides)

            # Filter data
            filtered_data = filter_kast(df, team_name=selected_team, side=selected_side)

            # Display data
            st.write("### Filtered KAST Statistics")
            st.dataframe(filtered_data)
        except Exception as e:
            st.error(f"Error processing demo file: {e}")

if __name__ == "__main__":
    main()
