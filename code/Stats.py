import pandas as pd
from awpy import Demo
from awpy.stats import kast, adr, rating

def parse_demo_file(demo_path):
    """
    Parse a .dem file and calculate player stats (kills, assists, deaths, KAST, ADR, Rating 2.0, Impact).

    Parameters:
        demo_path (str): Path to the demo file.

    Returns:
        dict: A dictionary containing 'combined_stats' (player stats) and 'kills_df' (raw kills data).
    """
    # Parse the demo file
    demo = Demo(demo_path)
    kills_df = demo.kills

    # Ensure positional data is present in kills_df
    positional_columns = ["attacker_pos_x", "attacker_pos_y", "victim_pos_x", "victim_pos_y"]
    for col in positional_columns:
        if col not in kills_df.columns:
            kills_df[col] = None  # Fill with None if not available

    # Calculate kills, assists, and deaths
    player_stats = (
        kills_df.groupby(["attacker_name", "attacker_team_name", "attacker_team_clan_name"])
        .agg(kills=("attacker_name", "count"), assists=("assister_name", "count"))
        .reset_index()
        .rename(
            columns={
                "attacker_name": "player_name",
                "attacker_team_name": "team_name",
                "attacker_team_clan_name": "clan_name",
            }
        )
    )

    deaths_stats = (
        kills_df.groupby(["victim_name", "victim_team_name", "victim_team_clan_name"])
        .agg(deaths=("victim_name", "count"))
        .reset_index()
        .rename(
            columns={
                "victim_name": "player_name",
                "victim_team_name": "team_name",
                "victim_team_clan_name": "clan_name",
            }
        )
    )

    final_stats = pd.merge(
        player_stats, deaths_stats, on=["player_name", "team_name", "clan_name"], how="outer"
    ).fillna(0)

    final_stats["kills"] = final_stats["kills"].astype(int)
    final_stats["assists"] = final_stats["assists"].astype(int)
    final_stats["deaths"] = final_stats["deaths"].astype(int)

    # Add "Both" side
    both_stats = (
        final_stats.groupby(["player_name", "clan_name"])
        .agg(kills=("kills", "sum"), assists=("assists", "sum"), deaths=("deaths", "sum"))
        .reset_index()
        .assign(team_name="Both")
    )

    combined_stats = pd.concat([final_stats, both_stats], ignore_index=True)
    combined_stats = combined_stats.sort_values(by=["team_name", "player_name"]).reset_index(drop=True)

    # Add KAST
    kast_stats = kast(demo)
    kast_df = (
        pd.DataFrame(kast_stats)
        .rename(columns={"name": "player_name", "team_name": "team_name", "kast": "kast_percentage"})
        .drop(columns=["steamid"])
    )
    kast_df["team_name"] = kast_df["team_name"].replace("all", "Both")

    combined_stats = pd.merge(combined_stats, kast_df, on=["player_name", "team_name"], how="left").fillna(0)

    # Add ADR
    adr_stats = adr(demo)
    adr_df = (
        pd.DataFrame(adr_stats)
        .rename(columns={"name": "player_name", "team_name": "team_name", "dmg": "total_damage", "adr": "average_damage_per_round"})
        .drop(columns=["steamid", "n_rounds"])
    )
    adr_df["team_name"] = adr_df["team_name"].replace("all", "Both")

    combined_stats = pd.merge(combined_stats, adr_df, on=["player_name", "team_name"], how="left").fillna(0)

    # Add Rating 2.0 and Impact
    rating_stats = rating(demo)
    rating_df = (
        pd.DataFrame(rating_stats)
        .rename(columns={"name": "player_name", "team_name": "team_name", "rating": "rating_2.0", "impact": "impact"})
        .drop(columns=["steamid", "n_rounds"])
    )
    rating_df["team_name"] = rating_df["team_name"].replace("all", "Both")

    combined_stats = pd.merge(combined_stats, rating_df, on=["player_name", "team_name"], how="left").fillna(0)

    # Return both the combined stats and kills dataframe
    return {"combined_stats": combined_stats, "kills_df": kills_df}


def get_game_events(demo_path, dataset_type, selected_columns=None):
    """
    Extract specific game event datasets from a demo file with selected columns.

    Parameters:
        demo_path (str): Path to the demo file.
        dataset_type (str): The type of dataset to extract ('kills', 'damages', 'bomb', 'grenades', 'smokes', 'infernos').
        selected_columns (list): A list of columns to display (optional).

    Returns:
        pd.DataFrame: A filtered DataFrame with the selected columns.
    """
    # Parse the demo file
    demo = Demo(demo_path)

    # Map dataset types to demo attributes
    dataset_map = {
        "kills": demo.kills,
        "damages": demo.damages,
        "bomb": demo.bomb,
        "grenades": demo.grenades,
        "smokes": demo.smokes,
        "infernos": demo.infernos,
    }

    if dataset_type not in dataset_map:
        raise ValueError(f"Invalid dataset type: {dataset_type}")

    # Get the dataset
    data = dataset_map[dataset_type]
    if data is None or data.empty:
        return pd.DataFrame()  # Return empty DataFrame if no data exists

    # Filter columns if specified
    if selected_columns:
        return data[selected_columns]
    return data

def parse_game_events(demo_path):
    """
    Parses game events (kills, damages, bomb events, grenades, smokes, and infernos)
    from a .dem file and returns structured DataFrames.

    Parameters:
        demo_path (str): Path to the demo file.

    Returns:
        dict: A dictionary containing DataFrames for game events.
    """
    demo = Demo(demo_path)

    # Function to extract specific columns from a DataFrame if it exists
    def get_columns(df, columns):
        if df is not None and not df.empty:
            return df[columns]
        else:
            return pd.DataFrame(columns=columns)

    # Extract kills
    kills_columns = [
        "tick", "attacker_name", "victim_name", "weapon", "headshot",
        "penetrated", "thrusmoke", "attacker_team_clan_name", "victim_team_clan_name"
    ]
    kills_df = get_columns(demo.kills, kills_columns)

    # Extract damages
    damages_columns = [
        "tick", "attacker_name", "victim_name", "weapon", "dmg_health",
        "dmg_armor", "attacker_team_clan_name", "victim_team_clan_name"
    ]
    damages_df = get_columns(demo.damages, damages_columns)

    # Extract bomb events
    bomb_columns = ["tick", "event", "site", "X", "Y", "Z", "round"]
    bomb_df = get_columns(demo.bomb, bomb_columns)

    # Extract grenades
    grenades_columns = ["tick", "grenade_type", "thrower", "X", "Y", "Z", "round"]
    grenades_df = get_columns(demo.grenades, grenades_columns)

    # Extract smokes
    smokes_columns = [
        "start_tick", "end_tick", "thrower_name", "thrower_team_clan_name", "X", "Y", "Z", "round"
    ]
    smokes_df = get_columns(demo.smokes, smokes_columns)

    # Extract infernos
    infernos_columns = [
        "start_tick", "end_tick", "thrower_name", "thrower_team_clan_name", "X", "Y", "Z", "round"
    ]
    infernos_df = get_columns(demo.infernos, infernos_columns)

    # Combine all into a dictionary
    return {
        "kills": kills_df,
        "damages": damages_df,
        "bomb_events": bomb_df,
        "grenades": grenades_df,
        "smokes": smokes_df,
        "infernos": infernos_df
    }
