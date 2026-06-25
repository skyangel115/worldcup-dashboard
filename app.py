import streamlit as st

st.set_page_config(page_title="World Cup Dashboard", layout="wide")

st.title("🌍 FIFA World Cup 2026 Group Dashboard")
st.write("Choose a group to view standings, match matrix, and remaining matches.")
st.caption(
    "⚠ Scenario percentages are based on simulated scorelines from 0–7 goals per team and represent scenario frequency, not real-world match probabilities."
)

# =====================
# Load Libraries
# =====================

import pandas as pd
import requests
import re
from io import StringIO

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
group_options = {
    g: f"Group {g} — {', '.join(groups[g])}"
    for g in sorted(groups.keys())
}

selected_group_label = st.selectbox(
    "Group",
    list(group_options.keys()),
    format_func=lambda g: group_options[g]
)

selected_group = selected_group_label
#st.write("Selected group:", selected_group)

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

    finished = len(remaining_games) == 0
    final_order = list(table.index)

    for team in teams:
        top2_prob = top2_count[team] / total_outcomes * 100
        third_prob = third_count[team] / total_outcomes * 100
        first_prob = first_count[team] / total_outcomes * 100

        probabilities[team] = round(top2_prob, 1)
        first_probabilities[team] = round(first_prob, 1)
        
        if finished:
            position = final_order.index(team) + 1

            if position == 1:
                statuses[team] = "🥇 Winner"
            elif position == 2:
                statuses[team] = "🥈 Runner-up"
            elif position == 3:
                statuses[team] = "🥉 Third Place"
            else:
                statuses[team] = "❌ Fourth Place"

        else:
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

    statuses, probabilities, first_probabilities = calculate_group_status_and_probability(
        selected_group,
        table,
        matrix
    )

    table["Status"] = [statuses[team] for team in table.index]
    table["1st Scenario %"] = [first_probabilities[team] for team in table.index]
    table["Top 2 Scenario %"] = [probabilities[team] for team in table.index]

    remaining_count = (matrix.values == "⏳").sum() // 2

    if remaining_count == 0:
        st.success(f"Group {selected_group} finished")
    else:
        st.info(f"Group {selected_group}: {remaining_count} matches remaining")

    st.markdown("### Group Summary")

    summary_items = [
        ("🥇 Leader", table.index[0]),
        ("🥈 2nd Place", table.index[1]),
        ("🥉 3rd Place", table.index[2]),
        ("🔻 Bottom", table.index[3]),
    ]

    summary_cols = st.columns(4)

    border_colors = ["#0057B8", "#2BA84A", "#F4A300", "#D7263D"]
    background_colors = ["#F5FAFF", "#F4FCF6", "#FFFAF2", "#FFF5F5"]

    for i, (col, (label, team)) in enumerate(zip(summary_cols, summary_items)):

        border_color = border_colors[i]
        background = background_colors[i]

        pts = table.loc[team, "Pts"]
        gd = table.loc[team, "GD"]
        gf = table.loc[team, "GF"]
        status = table.loc[team, "Status"]

        gd_text = f"+{gd}" if gd > 0 else str(gd)

        with col:
            card_html = f"""
<div style="
background:{background};
border:1px solid #e5e7eb;
border-top:7px solid {border_color};
border-radius:16px;
padding:18px;
box-shadow:0 4px 12px rgba(0,0,0,0.06);
min-height:170px;
">

<div style="
font-size:14px;
color:#6b7280;
margin-bottom:10px;
">
{label}
</div>

<div style="
font-size:30px;
font-weight:700;
margin-bottom:14px;
color:#222;
">
{team}
</div>

<div style="
font-size:15px;
line-height:2;
color:#374151;
">
<b>Pts</b> {pts}<br>
<b>GD</b> {gd_text}<br>
<b>GF</b> {gf}
</div>

<hr style="
border:none;
border-top:1px solid #dddddd;
margin:12px 0;
">

<div style="
font-size:16px;
font-weight:600;
">
{status}
</div>

</div>
"""

            st.markdown(card_html, unsafe_allow_html=True)

    st.subheader(f"Group {selected_group} Standings")
    standings_df = table.reset_index().rename(columns={"index": "Team"})

    row_colors = [
        "#E8F6EF",  # 1st
        "#EEF7FF",  # 2nd
        "#FFF7E8",  # 3rd
        "#FFF1F2"   # 4th
    ]

    html = """<div style="width:100%; overflow-x:auto;">
    <table style="
        width:100%;
        border-collapse:separate;
        border-spacing:0;
        border-radius:14px;
        overflow:hidden;
        box-shadow:0 4px 14px rgba(0,0,0,0.08);
        font-size:14px;
    ">
    <thead>
    <tr style="background:#1f4e79;color:white;">
    """

    for col in standings_df.columns:
        html += f"""
        <th style="
            padding:12px 10px;
            text-align:center;
            font-weight:700;
            border-bottom:3px solid #F4A300;
            white-space:nowrap;
        ">{col}</th>
        """

    html += """
    </tr>
    </thead>
    <tbody>
    """

    for i, row in standings_df.iterrows():
        bg = row_colors[i] if i < len(row_colors) else "#ffffff"

        html += f"""
        <tr style="background:{bg};">
        """

        for col in standings_df.columns:
            value = row[col]

            if col in ["1st Scenario %", "Top 2 Scenario %"]:
                value = f"{value:.1f}"

            weight = "700" if col in ["Team", "Pts", "Status"] else "400"

            html += f"""
            <td style="
                padding:12px 10px;
                text-align:center;
                border-bottom:1px solid #e5e7eb;
                border-right:1px solid #e5e7eb;
                font-weight:{weight};
                white-space:nowrap;
            ">{value}</td>
            """

        html += """
        </tr>
        """

    html += """
    </tbody>
    </table>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)

    # =====================
    # Matrix + Match List
    # =====================
    col1, col2 = st.columns([1.6, 0.8])

    with col1:
        st.subheader(f"Group {selected_group} Match Matrix")
        st.dataframe(
            matrix.reset_index().rename(columns={"index": ""}),
            use_container_width=True,
            hide_index=True
        )

    with col2:
        st.subheader("Matches")

        played = []
        for g, team1, score1, team2, score2 in matches:
            if g == selected_group:
                played.append(f"✅ {team1} {score1}-{score2} {team2}")

        remaining = []
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                t1 = teams[i]
                t2 = teams[j]
                if matrix.loc[t1, t2] == "⏳":
                    remaining.append(f"⏳ {t1} vs {t2}")

        played_html = "<br>".join(played) if played else "No played matches yet"
        remaining_html = "<br>".join(remaining) if remaining else "✅ No remaining matches"

        st.markdown("#### Played Matches")
        st.markdown(
            f"""
            <div style="
                background:#f8f9fa;
                padding:14px;
                border-radius:12px;
                line-height:2;
                border:1px solid #e9ecef;
            ">
                {played_html}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("#### Remaining Matches")
        st.markdown(
            f"""
            <div style="
                background:#fff3cd;
                padding:14px;
                border-radius:12px;
                line-height:2;
                border:1px solid #ffe69c;
            ">
                {remaining_html}
            </div>
            """,
            unsafe_allow_html=True
        )

    # =====================
    # Top 2 Scenario Chart
    # =====================
    st.subheader(f"Group {selected_group} Top 2 Qualification Chance")

    chart_col, _ = st.columns([0.55, 0.45])

    with chart_col:
        chance_df = table[["Top 2 Scenario %"]].sort_values(
            "Top 2 Scenario %",
            ascending=False
        )

        for team, row in chance_df.iterrows():
            prob = row["Top 2 Scenario %"]

            st.markdown(
                f"""
                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                    margin-top:12px;
                    font-size:16px;
                ">
                    <span><b>{team}</b></span>
                    <span>{prob:.1f}%</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.progress(min(max(prob / 100, 0), 1))





show_group(selected_group)

