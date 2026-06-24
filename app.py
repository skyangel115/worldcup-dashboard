import streamlit as st

st.set_page_config(page_title="World Cup Dashboard", layout="wide")

st.title("🌍 World Cup Group Dashboard")
st.write("Choose a group to view standings, match matrix, and remaining matches.")

# =====================
# Load Libraries
# =====================

import pandas as pd
import requests
import re
from io import StringIO
import matplotlib.pyplot as plt

# =====================
#Load data from Wikipedia
# =====================

url = "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"

headers = {
    "User-Agent": "Mozilla/5.0"
}

html = requests.get(url, headers=headers).text

tables = pd.read_html(StringIO(html))

standing_tables = []

for i, table in enumerate(tables):
    cols = list(table.columns)

    if any("Team" in str(c) for c in cols) and any("Pts" in str(c) for c in cols):
        standing_tables.append(i)

# =====================
# Build Group Information
# =====================

standing_tables = standing_tables[:12]

groups = {}

for group_label, table_idx in zip(list("ABCDEFGHIJKL"), standing_tables):
    table = tables[table_idx]

    team_col = [c for c in table.columns if "Team" in str(c)][0]

    teams = (
        table[team_col]
        .astype(str)
        .str.replace(r"\s*\(.*?\)", "", regex=True)
        .str.strip()
        .tolist()
    )

    groups[group_label] = teams
selected_group = st.selectbox("Group", sorted(groups.keys()))
st.write("Selected group:", selected_group)

# =====================
# Extract Match Results
# =====================

matches = []

match_info = {}

for i, table in enumerate(tables):
    if table.shape[1] < 3:
        continue

    team1 = str(table.columns[0]).strip()
    score = str(table.columns[1]).strip()
    team2 = str(table.columns[2]).strip()

    if not re.match(r"^\d+\s*[–-]\s*\d+$", score):
        continue

    s1, s2 = re.split(r"[–-]", score)
    s1 = int(s1.strip())
    s2 = int(s2.strip())

    group_found = None

    for g, team_list in groups.items():
        if team1 in team_list and team2 in team_list:
            group_found = g
            break

    if group_found is not None:
        matches.append((group_found, team1, s1, team2, s2))
        match_key = tuple(sorted([team1, team2]))
        match_info[match_key] = {
            "Group": group_found,
            "Score": f"{s1}-{s2}",
            "Status": "Played"
        }
  
for i, table in enumerate(tables):
    if table.shape[1] < 3:
        continue

    team1 = str(table.columns[0]).strip()
    middle = str(table.columns[1]).strip()
    team2 = str(table.columns[2]).strip()

    if not middle.startswith("Match"):
        continue

    group_found = None

    for g, team_list in groups.items():
        if team1 in team_list and team2 in team_list:
            group_found = g
            break

    if group_found is not None:
        match_key = tuple(sorted([team1, team2]))
        match_info[match_key] = {
            "Group": group_found,
            "Score": "⏳",
            "Status": "Remaining"
        }

# =====================
# Dashboard Functions
# =====================

from itertools import product

def rank_with_head_to_head(sim, all_matches, group):
    ranking = sim.copy()

    ranking = ranking.sort_values(
        ["Pts", "GD", "GF"],
        ascending=False
    )

    final_order = []

    for pts, tied in ranking.groupby("Pts", sort=False):
        tied_teams = list(tied.index)

        if len(tied_teams) == 1:
            final_order.extend(tied_teams)
            continue

        h2h = pd.DataFrame(
            0,
            index=tied_teams,
            columns=["H2H_Pts", "H2H_GD", "H2H_GF"]
        )

        for g, t1, s1, t2, s2 in all_matches:
            if g != group:
                continue

            if t1 in tied_teams and t2 in tied_teams:
                h2h.loc[t1, "H2H_GF"] += s1
                h2h.loc[t1, "H2H_GD"] += s1 - s2

                h2h.loc[t2, "H2H_GF"] += s2
                h2h.loc[t2, "H2H_GD"] += s2 - s1

                if s1 > s2:
                    h2h.loc[t1, "H2H_Pts"] += 3
                elif s1 < s2:
                    h2h.loc[t2, "H2H_Pts"] += 3
                else:
                    h2h.loc[t1, "H2H_Pts"] += 1
                    h2h.loc[t2, "H2H_Pts"] += 1

        tied_rank = ranking.loc[tied_teams].join(h2h)

        tied_rank = tied_rank.sort_values(
            ["H2H_Pts", "H2H_GD", "H2H_GF", "GD", "GF"],
            ascending=False
        )

        final_order.extend(list(tied_rank.index))

    ranked = ranking.loc[final_order]

    return ranked

def calculate_group_status_and_probability(group, table, matrix):
    teams = list(table.index)

    remaining_games = []

    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            t1 = teams[i]
            t2 = teams[j]

            if matrix.loc[t1, t2] == "⏳":
                remaining_games.append((t1, t2))

    possible_scores = []

    for a in range(8):
        for b in range(8):
            possible_scores.append((a,b))

    top2_count = {team: 0 for team in teams}
    third_count = {team: 0 for team in teams}
    first_count = {team: 0 for team in teams}
    total_outcomes = 0

    outcomes = list(product(possible_scores, repeat=len(remaining_games)))

    for outcome_set in outcomes:
        sim = table[["MP","W","D","L","GF","GA","GD","Pts"]].copy()
        sim_matches = matches.copy()

        for (t1, t2), (s1, s2) in zip(remaining_games, outcome_set):

            sim_matches.append((group, t1, s1, t2, s2))

            sim.loc[t1, "MP"] += 1
            sim.loc[t2, "MP"] += 1

            sim.loc[t1, "GF"] += s1
            sim.loc[t1, "GA"] += s2
            sim.loc[t2, "GF"] += s2
            sim.loc[t2, "GA"] += s1

            if s1 > s2:
                sim.loc[t1, "W"] += 1
                sim.loc[t2, "L"] += 1
                sim.loc[t1, "Pts"] += 3

            elif s1 < s2:
                sim.loc[t2, "W"] += 1
                sim.loc[t1, "L"] += 1
                sim.loc[t2, "Pts"] += 3

            else:
                sim.loc[t1, "D"] += 1
                sim.loc[t2, "D"] += 1
                sim.loc[t1, "Pts"] += 1
                sim.loc[t2, "Pts"] += 1

        sim["GD"] = sim["GF"] - sim["GA"]

        sim = rank_with_head_to_head(sim, sim_matches, group)

        first_team = sim.index[0]
        first_count[first_team] += 1

        top2 = set(sim.index[:2])
        third_team = sim.index[2]

        for team in top2:
            top2_count[team] += 1

        third_count[third_team] += 1

        total_outcomes += 1

    probabilities = {}
    first_probabilities = {}
    statuses = {}

    for team in teams:
        top2_prob = top2_count[team] / total_outcomes * 100
        third_prob = third_count[team] / total_outcomes * 100
        first_prob = first_count[team] / total_outcomes * 100

        probabilities[team] = round(top2_prob, 1)
        first_probabilities[team] = round(first_prob, 1)

        if first_prob == 100:
            statuses[team] = "🥇 1st Locked"
        elif top2_prob == 100:
            statuses[team] = "🟢 Top 2 Locked"
        elif top2_prob > 0:
            statuses[team] = "🟡 Top 2 Possible"
        elif third_prob > 0:
            statuses[team] = "🟠 3rd Possible"
        else:
            statuses[team] = "🔴 Eliminated"

    return statuses, probabilities, first_probabilities

def show_group(selected_group):
    teams = groups[selected_group]

# =====================
# Group Standings
# =====================
    table = pd.DataFrame(
        0,
        index=teams,
        columns=["MP","W","D","L","GF","GA","GD","Pts"]
    )

    for g, team1, score1, team2, score2 in matches:
        if g != selected_group:
            continue

        table.loc[team1, "MP"] += 1
        table.loc[team2, "MP"] += 1

        table.loc[team1, "GF"] += score1
        table.loc[team1, "GA"] += score2
        table.loc[team2, "GF"] += score2
        table.loc[team2, "GA"] += score1

        if score1 > score2:
            table.loc[team1, "W"] += 1
            table.loc[team2, "L"] += 1
            table.loc[team1, "Pts"] += 3

        elif score1 < score2:
            table.loc[team2, "W"] += 1
            table.loc[team1, "L"] += 1
            table.loc[team2, "Pts"] += 3

        else:
            table.loc[team1, "D"] += 1
            table.loc[team2, "D"] += 1
            table.loc[team1, "Pts"] += 1
            table.loc[team2, "Pts"] += 1

    table["GD"] = table["GF"] - table["GA"]

    table = rank_with_head_to_head(table, matches, selected_group)

    st.subheader(f"Group {selected_group} Standings")
    st.dataframe(
        table.reset_index().rename(columns={"index": "Team"}),
        use_container_width=True,
        hide_index=True
    )
    # =====================
    # Match Matrix
    # =====================
    matrix = pd.DataFrame(
        "⏳",
        index=teams,
        columns=teams
    )

    for team in teams:
        matrix.loc[team, team] = "—"

    for g, team1, score1, team2, score2 in matches:
        if g != selected_group:
            continue

        matrix.loc[team1, team2] = f"{score1}-{score2}"
        matrix.loc[team2, team1] = f"{score2}-{score1}"
    st.subheader(f"Group {selected_group} Match Matrix")

    st.dataframe(
        matrix.reset_index().rename(columns={"index": ""}),
        use_container_width=True,
        hide_index=True
    )







show_group(selected_group)

