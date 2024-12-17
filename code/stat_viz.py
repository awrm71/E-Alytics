import pandas as pd
import plotly.express as px
import streamlit as st

# Function to generate kill details with bold labels
def generate_kill_details(group):
    details = []
    for i, row in enumerate(group.itertuples(), 1):
        details.append(
            f"<b>Kill {i}:</b> Weapon: {row.weapon}, Damage: {row.dmg_health}, Headshot: {row.headshot}"
        )
    return "<br>".join(details)

# Function to process kills data for heatmaps
def process_kills_data(kills_df):
    required_columns = [
        "attacker_team_clan_name", "victim_team_clan_name",
        "attacker_name", "victim_name", "weapon", "dmg_health", "headshot"
    ]
    for col in required_columns:
        if col not in kills_df.columns:
            raise ValueError(f"Missing required column: {col} in kills_df")

    # Filter out team kills or self-kills
    filtered_kills_df = kills_df[
        kills_df["attacker_team_clan_name"] != kills_df["victim_team_clan_name"]
    ]

    def process_team_data(team_name):
        team_kills = filtered_kills_df[filtered_kills_df["attacker_team_clan_name"] == team_name]
        head_to_head = (
            team_kills.groupby(["attacker_name", "victim_name"])
            .agg(
                kills=("attacker_name", "count"),
                details=("weapon", lambda x: generate_kill_details(team_kills.loc[x.index])),
            )
            .reset_index()
        )
        heatmap_data = head_to_head.pivot(index="attacker_name", columns="victim_name", values="kills").fillna(0)
        hover_data = head_to_head.pivot(index="attacker_name", columns="victim_name", values="details").fillna("")
        return heatmap_data, hover_data

    clan_names = filtered_kills_df["attacker_team_clan_name"].unique()
    if len(clan_names) < 2:
        raise ValueError("Expected at least 2 clans in the data. Check the input data.")

    team1_heatmap_data, team1_hover_data = process_team_data(clan_names[0])
    team2_heatmap_data, team2_hover_data = process_team_data(clan_names[1])

    return (team1_heatmap_data, team1_hover_data), (team2_heatmap_data, team2_hover_data)


# Function to combine heatmap data from multiple matches
def combine_heatmaps(kills_data_list):
    combined_kills_df = pd.concat(kills_data_list, ignore_index=True)
    return process_kills_data(combined_kills_df)


# Function to create visuals for Streamlit
def create_heatmap_visuals(team1_data, team2_data, team1_name, team2_name):
    team1_heatmap_data, team1_hover_data = team1_data
    team2_heatmap_data, team2_hover_data = team2_data

    st.header(f"{team1_name} Heatmap")
    fig1 = px.imshow(
        team1_heatmap_data,
        labels=dict(x="Victim", y="Attacker", color="Kills"),
        title=f"{team1_name} Head-to-Head Kills",
        text_auto=True,
        color_continuous_scale="Blues",
    )
    fig1.update_traces(
        hovertemplate="<b>Attacker:</b> %{y}<br><b>Victim:</b> %{x}<br><b>Kills:</b> %{z}<br><b>Details:</b><br>%{customdata}",
        customdata=team1_hover_data.values,
    )
    st.plotly_chart(fig1)

    st.header(f"{team2_name} Heatmap")
    fig2 = px.imshow(
        team2_heatmap_data,
        labels=dict(x="Victim", y="Attacker", color="Kills"),
        title=f"{team2_name} Head-to-Head Kills",
        text_auto=True,
        color_continuous_scale="Reds",
    )
    fig2.update_traces(
        hovertemplate="<b>Attacker:</b> %{y}<br><b>Victim:</b> %{x}<br><b>Kills:</b> %{z}<br><b>Details:</b><br>%{customdata}",
        customdata=team2_hover_data.values,
    )
    st.plotly_chart(fig2)
