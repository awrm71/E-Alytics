import pytest
import pandas as pd

import streamlit as st
import os
import sys

# Add the project root directory to PYTHONPATH
# Add project root and code folder to PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
code_folder = os.path.join(project_root, "code")
sys.path.insert(0, code_folder)  # Add 'code' directory first
sys.path.insert(0, project_root)  # Add project root afterward

print("Updated PYTHONPATH:", sys.path)  # Debugging to confirm updated paths

# Import functions after adjusting PYTHONPATH
from code.E_alytics import combine_game_events, download_csv_button

# Mock data for testing
@pytest.fixture
def mock_parsed_matches():
    """Fixture for mock parsed matches with game events."""
    return {
        "match1": {
            "game_events": {
                "kills": pd.DataFrame({"player": ["Player1", "Player2"], "kills": [5, 7]}),
                "damages": pd.DataFrame({"player": ["Player1"], "damage": [100]}),
                "bomb_events": pd.DataFrame(),
                "grenades": pd.DataFrame(),
                "smokes": pd.DataFrame(),
                "infernos": pd.DataFrame(),
            }
        },
        "match2": {
            "game_events": {
                "kills": pd.DataFrame({"player": ["Player3"], "kills": [4]}),
                "damages": pd.DataFrame({"player": ["Player3"], "damage": [120]}),
                "bomb_events": pd.DataFrame(),
                "grenades": pd.DataFrame(),
                "smokes": pd.DataFrame(),
                "infernos": pd.DataFrame(),
            }
        },
    }


def test_combine_game_events(mock_parsed_matches):
    """Test combining game events across multiple matches."""
    combined_events = combine_game_events(mock_parsed_matches)

    # Check that combined DataFrames exist for each game event type
    assert "kills" in combined_events and "damages" in combined_events
    assert isinstance(combined_events["kills"], pd.DataFrame)
    assert isinstance(combined_events["damages"], pd.DataFrame)

    # Validate combined results
    assert combined_events["kills"].shape[0] == 3  # Two from match1, one from match2
    assert combined_events["damages"].shape[0] == 2  # One from match1, one from match2

    # Check empty events are skipped
    assert "bomb_events" in combined_events and combined_events["bomb_events"].empty


def test_download_csv_button(monkeypatch):
    """Test Streamlit download button functionality."""
    mock_df = pd.DataFrame({"Column1": [1, 2], "Column2": [3, 4]})
    mock_label = "Test Data"
    mock_key = "test_csv_button"

    # Mock Streamlit download button behavior
    class MockStreamlit:
        def __init__(self):
            self.download_button_called = False

        def download_button(self, **kwargs):
            self.download_button_called = True
            assert kwargs["label"] == f"Download {mock_label} as CSV"
            assert kwargs["file_name"] == "test_data.csv"
            assert kwargs["mime"] == "text/csv"
            assert "data" in kwargs

    mock_st = MockStreamlit()
    monkeypatch.setattr(st, "download_button", mock_st.download_button)

    # Call the function
    download_csv_button(mock_df, mock_label, mock_key)

    # Assert the button was triggered
    assert mock_st.download_button_called, "Streamlit download_button was not triggered"
