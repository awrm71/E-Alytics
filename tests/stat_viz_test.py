import sys
import os

# Add the project root directory to PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)  # Add to the beginning of sys.path

print("Updated PYTHONPATH:", sys.path)  # Debugging to confirm project root is added

import pytest
import pandas as pd
from code.stat_viz import (
    generate_kill_details,
    process_kills_data,
    combine_heatmaps
)


@pytest.fixture
def mock_kills_df():
    """Fixture for mock kills DataFrame."""
    data = {
        "attacker_team_clan_name": ["ClanA", "ClanA", "ClanB", "ClanB"],
        "victim_team_clan_name": ["ClanB", "ClanB", "ClanA", "ClanA"],
        "attacker_name": ["Player1", "Player2", "Player3", "Player4"],
        "victim_name": ["Player3", "Player4", "Player1", "Player2"],
        "weapon": ["AK-47", "M4A4", "AWP", "AK-47"],
        "dmg_health": [100, 90, 100, 100],
        "headshot": [True, False, True, True],
    }
    return pd.DataFrame(data)


def test_generate_kill_details(mock_kills_df):
    """Test generating formatted kill details."""
    group = mock_kills_df.iloc[:2]
    result = generate_kill_details(group)
    assert isinstance(result, str), "Kill details output should be a string"
    assert "<b>Kill 1:</b>" in result
    assert "Weapon: AK-47" in result
    assert "Damage: 100" in result
    assert "Headshot: True" in result


def test_process_kills_data(mock_kills_df):
    """Test processing kills data to create heatmaps."""
    (team1_data, team1_hover), (team2_data, team2_hover) = process_kills_data(mock_kills_df)

    # Validate the heatmap data is returned as DataFrames
    assert isinstance(team1_data, pd.DataFrame)
    assert isinstance(team1_hover, pd.DataFrame)
    assert isinstance(team2_data, pd.DataFrame)
    assert isinstance(team2_hover, pd.DataFrame)

    # Check dimensions of the DataFrame
    assert team1_data.shape == (2, 2), "Team1 heatmap dimensions are incorrect"
    assert team2_data.shape == (2, 2), "Team2 heatmap dimensions are incorrect"

    # Verify expected values
    assert team1_data.loc["Player1", "Player3"] == 1, "Kills count for Team 1 is incorrect"
    assert team2_data.loc["Player3", "Player1"] == 1, "Kills count for Team 2 is incorrect"

    # Test missing required columns
    with pytest.raises(ValueError, match="Missing required column"):
        invalid_df = mock_kills_df.drop(columns=["weapon"])
        process_kills_data(invalid_df)

    # Test insufficient clan names
    single_clan_df = mock_kills_df[mock_kills_df["attacker_team_clan_name"] == "ClanA"]
    with pytest.raises(ValueError, match="Expected at least 2 clans"):
        process_kills_data(single_clan_df)


def test_combine_heatmaps(mock_kills_df):
    """Test combining heatmaps from multiple matches."""
    kills_data_list = [mock_kills_df, mock_kills_df]
    combined_data = combine_heatmaps(kills_data_list)

    (team1_data, team1_hover), (team2_data, team2_hover) = combined_data

    # Validate combined results
    assert isinstance(team1_data, pd.DataFrame)
    assert isinstance(team2_data, pd.DataFrame)
    assert team1_data.sum().sum() == 4, "Combined kills count for Team 1 is incorrect"
    assert team2_data.sum().sum() == 4, "Combined kills count for Team 2 is incorrect"
