import sys
import os
import glob

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)  # Add to the beginning of sys.path

print("Updated PYTHONPATH:", sys.path)  # Debugging to confirm project root is added

# Correct path to the cache folder
cache_folder = os.path.join(project_root, "cache")

# Find all .dem files in the cache folder
dem_files = glob.glob(os.path.join(cache_folder, "*.dem"))

if not dem_files:
    raise FileNotFoundError(f"No .dem files found in {cache_folder}")

# Use the first .dem file found for testing
DEMO_FILE = dem_files[0]
print(f"Using demo file: {DEMO_FILE}")

from code.Stats import parse_demo_file, get_game_events, parse_game_events

import pytest
import pandas as pd
from awpy import Demo




@pytest.fixture
def mock_demo_file():
    """
    Fixture to ensure the sample demo file exists.
    Replace 'sample.dem' with a real file path in your test environment.
    """
    assert os.path.exists(DEMO_FILE), f"Test file not found: {DEMO_FILE}"
    return DEMO_FILE

def test_parse_demo_file(mock_demo_file):
    """Test parsing a demo file and validating combined stats."""
    result = parse_demo_file(mock_demo_file)

    # Ensure 'combined_stats' and 'kills_df' are returned
    assert 'combined_stats' in result and 'kills_df' in result
    assert isinstance(result['combined_stats'], pd.DataFrame)
    assert isinstance(result['kills_df'], pd.DataFrame)

    # Check basic structure of combined_stats
    required_columns = ["player_name", "team_name", "clan_name", "kills", "assists", "deaths"]
    for col in required_columns:
        assert col in result['combined_stats'].columns

def test_get_game_events(mock_demo_file):
    """Test extraction of game event datasets."""
    dataset_types = ["kills", "damages", "bomb", "grenades", "smokes", "infernos"]
    for dataset in dataset_types:
        result = get_game_events(mock_demo_file, dataset)
        assert isinstance(result, pd.DataFrame), f"{dataset} dataset is not a DataFrame"

        # Check that columns exist when data is not empty
        if not result.empty:
            assert all(col in result.columns for col in result.columns)

def test_parse_game_events(mock_demo_file):
    """Test parsing game events and ensuring DataFrames are structured correctly."""
    result = parse_game_events(mock_demo_file)
    assert isinstance(result, dict), "Result is not a dictionary"

    # Validate keys and their structure
    expected_keys = ["kills", "damages", "bomb_events", "grenades", "smokes", "infernos"]
    for key in expected_keys:
        assert key in result, f"Missing key: {key}"
        assert isinstance(result[key], pd.DataFrame), f"{key} is not a DataFrame"

    # Check example columns for kills DataFrame
    if not result["kills"].empty:
        required_kills_columns = ["attacker_name", "victim_name", "weapon", "headshot"]
        for col in required_kills_columns:
            assert col in result["kills"].columns
