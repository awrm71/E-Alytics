import pandas as pd
from awpy.plot import heatmap
import matplotlib.pyplot as plt


def extract_map_name_from_filename(file_name):
    """
    Extract the map name from the file name.
    Assumes the map name is part of the file name, e.g., 'g2-vs-heroic-m1-ancient.dem'.

    Parameters:
        file_name (str): The name of the demo file.

    Returns:
        str: The extracted map name with 'de_' prefix for compatibility.
    """
    return f"de_{file_name.split('-')[-1].replace('.dem', '')}"


import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator
from awpy.plot import heatmap

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator
from awpy.plot import heatmap

def generate_map_visuals(parsed_matches, selected_map, show_option):
    """
    Generate heatmaps for kills or deaths for a specific map.

    Parameters:
        parsed_matches (dict): Parsed match data.
        selected_map (str): Map name.
        show_option (str): Either 'kills' or 'deaths'.

    Returns:
        tuple: Matplotlib figures for Clan 1 and Clan 2.
    """
    clan1_points = []
    clan2_points = []

    for match_data in parsed_matches.values():
        kills_df = match_data["kills_df"]

        # Filter kills data for the selected map
        kills_on_map = kills_df[kills_df["map_name"] == selected_map]
        if kills_on_map.empty:
            continue

        # Extract clan names dynamically
        clans = kills_on_map["attacker_team_clan_name"].dropna().unique()
        if len(clans) >= 2:
            clan1, clan2 = clans[:2]
        else:
            continue

        # Collect points
        if show_option == "kills":
            clan1_points.extend(kills_on_map[kills_on_map["attacker_team_clan_name"] == clan1][["attacker_X", "attacker_Y"]].dropna().values.tolist())
            clan2_points.extend(kills_on_map[kills_on_map["attacker_team_clan_name"] == clan2][["attacker_X", "attacker_Y"]].dropna().values.tolist())
        elif show_option == "deaths":
            clan1_points.extend(kills_on_map[kills_on_map["victim_team_clan_name"] == clan1][["victim_X", "victim_Y"]].dropna().values.tolist())
            clan2_points.extend(kills_on_map[kills_on_map["victim_team_clan_name"] == clan2][["victim_X", "victim_Y"]].dropna().values.tolist())

    # Ensure points are valid
    if not clan1_points or not clan2_points:
        raise ValueError(f"No valid data to plot heatmap for {selected_map}.")

    # Function to format ticks as integers
    def integer_formatter(x, _):
        return f"{int(x)}" if x.is_integer() else ""

    # Generate heatmaps with color bar and proper tick range
    def create_heatmap(points, map_name, title):
        fig, ax = plt.subplots(figsize=(10, 6))  # Increase overall figure size here
        fig, ax = heatmap(
            map_name=map_name,
            points=points,
            method="hist",
            size=27,  # Adjust size for larger grid boxes
            cmap="coolwarm",
            alpha=0.7,
            vary_alpha=False,
        )

        if fig is None or ax is None:
            raise ValueError(f"Heatmap function failed for map: {map_name}")

        # Add title
        ax.set_title(title, fontsize=16, pad=20)

        # Adjust the color bar
        fig.subplots_adjust(right=0.9)  # Space for legend
        cbar = fig.colorbar(ax.collections[0], ax=ax, orientation='vertical', fraction=0.02, pad=0.03)

        # Set clean integer tick labels with proper positions
        cbar.locator = MaxNLocator(integer=True)
        cbar.formatter = FuncFormatter(integer_formatter)
        cbar.update_ticks()

        # Customize color bar ticks
        cbar.ax.yaxis.set_tick_params(color='white')
        plt.setp(cbar.ax.get_yticklabels(), color='white', fontsize=10)

        return fig

    # Create heatmaps for both clans
    fig1 = create_heatmap(clan1_points, selected_map, f"{clan1} Heatmap for {show_option.capitalize()} on {selected_map}")
    fig2 = create_heatmap(clan2_points, selected_map, f"{clan2} Heatmap for {show_option.capitalize()} on {selected_map}")

    return fig1, fig2








def get_available_maps(matches_data):
    """
    Retrieve a list of available maps from the matches data.

    Parameters:
        matches_data (dict): A dictionary of matches containing parsed stats and kills_df.

    Returns:
        list: A list of unique map names from all matches.
    """
    map_names = set()
    for match_name, match_data in matches_data.items():
        map_names.add(match_data["kills_df"]["map_name"].iloc[0])
    return sorted(map_names)


def create_tab_customizations(show_option="kills"):
    """
    Generate tab-based customizations for maps similar to Leetify.

    Parameters:
        show_option (str): The current show option (either 'kills' or 'deaths').

    Returns:
        str: The selected show option.
    """
    import streamlit as st

    with st.sidebar:
        st.write("### Map Customizations")
        tabs = st.radio(
            "Select Data to Display",
            options=["Kills", "Deaths"],
            index=0 if show_option == "kills" else 1,
        )

    return tabs.lower()
