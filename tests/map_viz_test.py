import pytest
import pandas as pd

import sys
import os

# Add the project root directory to PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)  # Add to the beginning of sys.path

print("Updated PYTHONPATH:", sys.path)  # Debugging to confirm project root is added

from code.map_viz import (
    extract_map_name_from_filename,
    generate_map_visuals,
    get_available_maps
)
import matplotlib.figure

@pytest.fixture
def mock_matches_data():
    """Fixture for mock match data to simulate parsed_matches."""
    data = {
        "match1": {
            "kills_df": pd.DataFrame({
                "map_name": ["de_ancient", "de_ancient"],
                "attacker_team_clan_name": ["ClanA", "ClanB"],
                "victim_team_clan_name": ["ClanB", "ClanA"],
                "attacker_X": [100, 200],
                "attacker_Y": [150, 250],
                "victim_X": [300, 400],
                "victim_Y": [350, 450],
            })
        },
        "match2": {
            "kills_df": pd.DataFrame({
                "map_name": ["de_inferno"],
                "attacker_team_clan_name": ["ClanA"],
                "victim_team_clan_name": ["ClanB"],
                "attacker_X": [500],
                "attacker_Y": [600],
                "victim_X": [700],
                "victim_Y": [800],
            })
        }
    }
    return data


def test_extract_map_name_from_filename():
    """Test extracting the map name from a demo file name."""
    assert extract_map_name_from_filename("g2-vs-heroic-m1-ancient.dem") == "de_ancient"
    assert extract_map_name_from_filename("navi-vs-faze-m2-inferno.dem") == "de_inferno"
    assert extract_map_name_from_filename("unknown.dem") == "de_unknown"


def test_generate_map_visuals(mock_matches_data):
    """Test generating map visuals for valid matches and maps."""
    selected_map = "de_ancient"
    show_option = "kills"

    # Generate heatmaps
    fig1, fig2 = generate_map_visuals(mock_matches_data, selected_map, show_option)

    # Validate that figures are Matplotlib Figure instances
    assert isinstance(fig1, matplotlib.figure.Figure)
    assert isinstance(fig2, matplotlib.figure.Figure)

    # Invalid map handling
    with pytest.raises(ValueError, match=f"No valid data to plot heatmap for de_invalid"):
        generate_map_visuals(mock_matches_data, "de_invalid", show_option)


def test_get_available_maps(mock_matches_data):
    """Test retrieving available maps from match data."""
    available_maps = get_available_maps(mock_matches_data)
    assert available_maps == ["de_ancient", "de_inferno"]
