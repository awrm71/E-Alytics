import streamlit as st
import pandas as pd
from Stats import parse_demo_file, parse_game_events
from stat_viz import combine_heatmaps, create_heatmap_visuals
from map_viz import (
    generate_map_visuals,
    extract_map_name_from_filename,
    get_available_maps,
    create_tab_customizations
)


def combine_game_events(parsed_matches):
    """
    Combines game events across multiple matches into unified DataFrames.

    Parameters:
        parsed_matches (dict): Parsed matches with game events.

    Returns:
        dict: Combined DataFrames for all game events.
    """
    combined_events = {key: [] for key in ["kills", "damages", "bomb_events", "grenades", "smokes", "infernos"]}

    for match_data in parsed_matches.values():
        for event_type, event_df in match_data["game_events"].items():
            combined_events[event_type].append(event_df)

    return {event: pd.concat(dfs, ignore_index=True) for event, dfs in combined_events.items() if dfs}


def download_csv_button(dataframe, label, key):
    """
    Adds a download button for a given DataFrame.

    Parameters:
        dataframe (pd.DataFrame): The DataFrame to download.
        label (str): Label for the download button.
        key (str): Unique key for Streamlit to avoid duplicate element errors.
    """
    if not dataframe.empty:
        csv = dataframe.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=f"Download {label} as CSV",
            data=csv,
            file_name=f"{label.replace(' ', '_').lower()}.csv",
            mime="text/csv",
            key=key,  # Unique key
        )



def main():
    st.title("Player Performance Viewer with Match Results")

    tournament_file = "cache/tournaments.csv"  # Adjust path based on screenshots
    matches_file = "cache/tournament_matches.csv"

    tournaments_df = pd.read_csv(tournament_file)
    matches_df = pd.read_csv(matches_file)

    # Tournament and Match Selection
    st.sidebar.write("## Tournament and Match Selection")
    selected_tournament = st.sidebar.selectbox(
        "Select Tournament", tournaments_df["Event Name"].unique()
    )

    # Filter matches for the selected tournament
    filtered_matches = matches_df[matches_df["Tournament"] == selected_tournament]

    selected_match = st.sidebar.selectbox(
        "Select Match",
        filtered_matches["Match Link"].index,  # Show indices for matches
        format_func=lambda x: f"{filtered_matches.loc[x, 'Team 1']} vs {filtered_matches.loc[x, 'Team 2']}"
    )

    # Display Match Info
    if not filtered_matches.empty:
        st.write("### Match Information")
        match_row = filtered_matches.loc[selected_match]
        st.write(f"**Tournament**: {selected_tournament}")
        st.write(f"**Matchup**: {match_row['Team 1']} vs {match_row['Team 2']}")
        st.write(f"**Score**: {match_row['Score']}")
        st.write(f"**Link to Match**: [View on HLTV]({match_row['Match Link']})")

    # Instructions for downloading files
    st.info("To download files, click the download button on the page located on the right side.")


    st.warning("If the files download as a compressed `.rar` file, you can use [7-Zip](https://www.7-zip.org/) to unzip them. "
               "Simply download and install 7-Zip, then right-click the file and choose 'Extract Here'. Once downloaded, you can upload the `.dem` files into"
               "this repository's `Cache` folder.")
    
    # Allow multiple .dem file uploads
    uploaded_files = st.sidebar.file_uploader(
        "Upload .dem files", type=["dem"], accept_multiple_files=True
    )

    if uploaded_files:
        # Initialize session state to store parsed matches
        if "parsed_matches" not in st.session_state:
            st.session_state["parsed_matches"] = {}

        # Process each uploaded file and store it in session state
        for uploaded_file in uploaded_files:
            if uploaded_file.name not in st.session_state["parsed_matches"]:
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.read())

                @st.cache_data(show_spinner=False)
                def process_demo_file_with_events(demo_path, file_name):
                    parsed_data = parse_demo_file(demo_path)
                    parsed_data["kills_df"]["map_name"] = extract_map_name_from_filename(file_name)
                    parsed_data["game_events"] = parse_game_events(demo_path)  # Add game events parsing
                    return parsed_data

                try:
                    # Parse the file and store results
                    parsed_data = process_demo_file_with_events(temp_path, uploaded_file.name)
                    st.session_state["parsed_matches"][uploaded_file.name] = parsed_data
                except Exception as e:
                    st.error(f"Error processing file {uploaded_file.name}: {e}")

        # Dropdown to select which match to view
        match_options = ["All Matches"] + list(st.session_state["parsed_matches"].keys())
        selected_match = st.sidebar.selectbox("Select Match to View", match_options)

        # Dropdown to switch between Summary Stats and Game Events
        data_view = st.sidebar.radio("Select Data View", ["Summary Stats", "Game Events"])

        if "kills_data_list" not in st.session_state or "combined_stats_list" not in st.session_state:
            st.session_state["kills_data_list"] = []
            st.session_state["combined_stats_list"] = []

        # Clear the lists to prevent duplicates
        st.session_state["kills_data_list"].clear()
        st.session_state["combined_stats_list"].clear()

        for match_name, parsed_data in st.session_state["parsed_matches"].items():
            st.session_state["kills_data_list"].append(parsed_data["kills_df"])
            st.session_state["combined_stats_list"].append(parsed_data["combined_stats"])

        kills_data_list = st.session_state["kills_data_list"]
        combined_stats_list = st.session_state["combined_stats_list"]


        if data_view == "Summary Stats":
            # Summary Stats Section
            st.write("### Summary Statistics Viewer")

            # Combine stats for "All Matches"
            all_combined_stats = pd.concat(combined_stats_list, ignore_index=True)
            numeric_columns = ["kills", "assists", "deaths", "n_rounds", "total_damage"]
            average_columns = ["kast_percentage", "average_damage_per_round", "rating_2.0", "impact"]

            all_combined_stats = (
                all_combined_stats.groupby(["player_name", "team_name", "clan_name"])
                .agg({**{col: "sum" for col in numeric_columns}, **{col: "mean" for col in average_columns}})
                .reset_index()
            )

            # Apply selected match or "All Matches"
            if selected_match == "All Matches":
                filtered_data = all_combined_stats.copy()
                kills_data = kills_data_list
            else:
                filtered_data = st.session_state["parsed_matches"][selected_match]["combined_stats"]
                kills_data = [st.session_state["parsed_matches"][selected_match]["kills_df"]]

            # Sidebar filters for dataset customization
            st.sidebar.write("### Dataset Customization")
            team_options = ["All Teams"] + sorted(filtered_data["clan_name"].unique().tolist())
            selected_team = st.sidebar.selectbox("Select Clan", team_options)
            selected_team = None if selected_team == "All Teams" else selected_team

            side_options = ["All Sides", "CT", "TERRORIST", "Both"]
            selected_side = st.sidebar.selectbox("Select Side", side_options)
            selected_side = None if selected_side == "All Sides" else selected_side

            # Apply filters
            if selected_team:
                filtered_data = filtered_data[filtered_data["clan_name"] == selected_team]
            if selected_side:
                filtered_data = filtered_data[filtered_data["team_name"] == selected_side]

            # Display the dataset
            st.write("### Filtered Player Statistics")
            st.dataframe(filtered_data)

            # Download filtered data
            download_csv_button(filtered_data, "Filtered Player Statistics", key="summary_stats_csv")



        elif data_view == "Game Events":
            # Game Events Section
            st.write("### Game Events Viewer")

            # Combine or select game events
            if selected_match == "All Matches":
                game_events = combine_game_events(st.session_state["parsed_matches"])
            else:
                game_events = st.session_state["parsed_matches"][selected_match]["game_events"]

            # Display each game event type in an expandable section
            for event_name, event_df in game_events.items():
                with st.expander(f"{event_name.replace('_', ' ').capitalize()} Data"):
                    if not event_df.empty:
                        st.dataframe(event_df)
                        # Download game event data
                        download_csv_button(event_df, f"{event_name.capitalize()} Data", key=f"{selected_match}_{event_name}_csv")

                    else:
                        st.write(f"No {event_name} data available for this match.")

        # Generate heatmaps for Summary Stats (remain static when switching views)
       # Ensure kills_data is initialized before views
        kills_data = []
        if selected_match == "All Matches":
            kills_data = [parsed_data["kills_df"] for parsed_data in st.session_state["parsed_matches"].values()]
        elif selected_match in st.session_state["parsed_matches"]:
            kills_data = [st.session_state["parsed_matches"][selected_match]["kills_df"]]



        # Generate heatmaps for Summary Stats (remain static when switching views)
        if kills_data:
            team1_data, team2_data = combine_heatmaps(kills_data)
            create_heatmap_visuals(
                team1_data,
                team2_data,
                team1_data[0].index.name or "Team 1",
                team2_data[0].index.name or "Team 2",
            )



        # Retrieve available maps and set customization options
        all_maps = get_available_maps(st.session_state["parsed_matches"])
        st.sidebar.write("### Map Customizations")
        selected_map = st.sidebar.selectbox("Select Map", all_maps)
        show_option = create_tab_customizations()

        # Generate map visuals
        if selected_map:
            try:
                # Retrieve team names dynamically from the kills_df
                clan1_name = st.session_state["parsed_matches"][list(st.session_state["parsed_matches"].keys())[0]]["kills_df"]["attacker_team_clan_name"].iloc[0]
                clan2_name = st.session_state["parsed_matches"][list(st.session_state["parsed_matches"].keys())[0]]["kills_df"]["victim_team_clan_name"].iloc[0]

                # Call the updated generate_map_visuals function
                map_visuals_clan1, map_visuals_clan2 = generate_map_visuals(
                    st.session_state["parsed_matches"],
                    selected_map,
                    show_option
                )

                st.write(f"### {clan1_name} Heatmap for {show_option.capitalize()} on {selected_map}")
                st.pyplot(map_visuals_clan1)

                st.write(f"### {clan2_name} Heatmap for {show_option.capitalize()} on {selected_map}")
                st.pyplot(map_visuals_clan2)
            except Exception as e:
                st.error(f"Error generating map visuals for {selected_map}: {e}")


if __name__ == "__main__":
    main()
