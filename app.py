import streamlit as st
import time

st.set_page_config(page_title="World Cup Dashboard", layout="wide")

st.title("🌍 FIFA World Cup 2026 Dashboard")

st.write("Track standings, qualification probabilities, and knockout progression throughout the tournament.")


# ---------- Hero ----------
#group_matches_completed = 72 if tournament_stage == "Round of 32" else "In Progress"
#group_status = "Completed" if tournament_stage == "Round of 32" else "Ongoing"

#st.markdown(
#    f"""
#<div style="
#background:linear-gradient(135deg,#F5FAFF,#EEF6FF);
#border:1px solid #D8E6F5;
#border-radius:18px;
#padding:22px 26px;
#margin-top:18px;
#margin-bottom:26px;
#box-shadow:0 4px 14px rgba(0,0,0,0.05);
#">

#<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:18px;">

#<div style="
#background:white;
#border:1px solid #D8E6F5;
#border-radius:16px;
#padding:22px;
#box-shadow:0 4px 12px rgba(0,0,0,0.04);
#">
#<div style="font-size:16px;color:#6b7280;font-weight:700;">📊 Groups</div>
#<div style="font-size:34px;font-weight:900;color:#1F4E79;margin-top:10px;">12</div>
#</div>

#<div style="
#background:white;
#border:1px solid #D6EFE2;
#border-radius:16px;
#padding:22px;
#box-shadow:0 4px 12px rgba(0,0,0,0.04);
#">
#<div style="font-size:16px;color:#6b7280;font-weight:700;">⚽ Group Matches</div>
#<div style="font-size:34px;font-weight:900;color:#16834A;margin-top:10px;">{group_matches_completed} / 72</div>
#</div>

#<div style="
#background:white;
#border:1px solid #E6D8FF;
#border-radius:16px;
#padding:22px;
#box-shadow:0 4px 12px rgba(0,0,0,0.04);
#">
#<div style="font-size:16px;color:#6b7280;font-weight:700;">🏁 Group Status</div>
#<div style="font-size:30px;font-weight:900;color:#7C3AED;margin-top:10px;">{group_status}</div>
#</div>

#<div style="
#background:white;
#border:1px solid #F7DFA8;
#border-radius:16px;
#padding:22px;
#box-shadow:0 4px 12px rgba(0,0,0,0.04);
#">
#<div style="font-size:16px;color:#6b7280;font-weight:700;">🏟️ Tournament</div>
#<div style="font-size:30px;font-weight:900;color:#B7791F;margin-top:10px;">{tournament_stage}</div>
#</div>

#</div>
#</div>
#""",
#    unsafe_allow_html=True,
#)

st.caption(
    "⚠ Scenario percentages are based on simulated scorelines from 0–7 goals per team and represent scenario frequency, not real-world match probabilities."
)

st.markdown("""
<style>
label[data-testid="stWidgetLabel"] p {
    font-size:24px;
    font-weight:900;
    margin-bottom:8px;
}

div[data-testid="stCaptionContainer"] p{
    font-size:16px !important;
    color:#5B6573 !important;
    line-height:1.5;
}

div.stButton > button{
    font-size:18px !important;
    font-weight:800 !important;
    min-height:48px !important;
    border-radius:14px !important;
}

div[data-testid="stSegmentedControl"]{
    margin-top:8px;
    margin-bottom:28px;
}

div[data-testid="stSegmentedControl"] button{
    font-size:19px !important;
    font-weight:850 !important;
    padding:15px 38px !important;
    min-height:60px !important;
    border-radius:16px !important;
    transition:all .2s ease;
}

div[data-testid="stSegmentedControl"] button:hover{
    transform:translateY(-2px);
    box-shadow:0 4px 10px rgba(0,0,0,.12);
}

div[data-testid="stSegmentedControl"] button[aria-pressed="true"]{
    background:#E6F0FF !important;
    color:#1F4E79 !important;
    border:1px solid #1F4E79 !important;
    font-weight:900 !important;
    box-shadow:0 4px 12px rgba(31,78,121,.35);
}

</style>
""", unsafe_allow_html=True)

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
# Data Preparation
# =====================

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
def get_group_remaining_count(group):
    teams = groups[group]
    remaining_count = 0

    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            match_key = tuple(sorted([teams[i], teams[j]]))

            if match_key in match_info and match_info[match_key]["Status"] == "Remaining":
                remaining_count += 1

    return remaining_count


st.markdown("### 🌍 Select Group")

selected_group = st.segmented_control(
    "Group",
    options=sorted(groups.keys()),
    label_visibility="collapsed"
)

if selected_group is None:
    selected_group = "A"


st.markdown("### 🏆 Group Overview")

group_cols = st.columns(4)

for idx, g in enumerate(sorted(groups.keys())):
    col = group_cols[idx % 4]

    is_selected = g == selected_group

    border_color = "#1F4E79" if is_selected else "#E5E7EB"
    border_width = "3px" if is_selected else "1px"
    background = "#F5FAFF" if is_selected else "#FFFFFF"
    shadow = "0 4px 14px rgba(0,0,0,.10)" if is_selected else "0 2px 8px rgba(0,0,0,.04)"
    title_icon = "🏆" if is_selected else "⚽"

    remaining_in_group = get_group_remaining_count(g)

    if remaining_in_group == 0:
        group_status_badge = """
<span style="background:#DCFCE7;color:#166534;padding:5px 10px;border-radius:999px;font-size:13px;font-weight:800;">
Completed
</span>
"""
    else:
        group_status_badge = f"""
<span style="background:#DBEAFE;color:#1D4ED8;padding:5px 10px;border-radius:999px;font-size:13px;font-weight:800;">
{remaining_in_group} left
</span>
"""

    ranked_teams = groups[g]
    team_lines = []

    for i, team in enumerate(ranked_teams):
        if i == 0:
            team_lines.append(f"🥇 {team}")
        elif i == 1:
            team_lines.append(f"🥈 {team}")
        elif i == 2:
            team_lines.append(f"🥉 {team}")
        else:
            team_lines.append(f"❌ {team}")

    teams_html = "<br>".join(team_lines)

    with col:
        st.markdown(
            f"""<div style="
background:{background};
border:{border_width} solid {border_color};
border-radius:16px;
padding:14px 16px;
margin-bottom:14px;
box-shadow:{shadow};
min-height:150px;
">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
<div style="font-size:21px;font-weight:800;color:#1f2937;">
{title_icon} Group {g}
</div>
{group_status_badge}
</div>

<div style="font-size:15px;font-weight:600;line-height:1.8;color:#374151;">
{teams_html}
</div>
</div>""",
            unsafe_allow_html=True
        )

st.markdown("---")

view = st.segmented_control(
    "Navigation",
    options=[
        "🌍 Group Stage",
        "🥉 Best Third-Placed Teams",
        "🏆 Knockout Stage"
    ],
    label_visibility="collapsed",
    default="🌍 Group Stage"
)

from itertools import product
POSSIBLE_SCORES = [(a, b) for a in range(8) for b in range(8)]

def rank_with_head_to_head(sim, all_matches, group):
    ranking = sim.copy()

    ranking = ranking.sort_values(
        ["Pts", "GD", "GF"],
        ascending=False
    )

    # 沒有同分直接回傳
    if ranking["Pts"].is_unique:
        return ranking

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
    #st.write(f"Calculating status/probability for Group {group}")
    


    teams = list(table.index)

    remaining_games = []

    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            t1 = teams[i]
            t2 = teams[j]

            if matrix.loc[t1, t2] == "⏳":
                remaining_games.append((t1, t2))
    if len(remaining_games) == 0:
        final_ranked = rank_with_head_to_head(
            table[["MP","W","D","L","GF","GA","GD","Pts"]].copy(),
            matches,
            group
        )

        statuses = {}
        probabilities = {}
        first_probabilities = {}

        for idx, team in enumerate(final_ranked.index):
            position = idx + 1

            probabilities[team] = 100.0 if position <= 2 else 0.0
            first_probabilities[team] = 100.0 if position == 1 else 0.0

            if position == 1:
                statuses[team] = "🥇 Winner"
            elif position == 2:
                statuses[team] = "🥈 Runner-up"
            elif position == 3:
                statuses[team] = "🥉 Third Place"
            else:
                statuses[team] = "❌ Fourth Place"

        return statuses, probabilities, first_probabilities

    top2_count = {team: 0 for team in teams}
    third_count = {team: 0 for team in teams}
    first_count = {team: 0 for team in teams}
    total_outcomes = 0

    base_group_matches = [m for m in matches if m[0] == group]

    start_time = time.time()

    for outcome_set in product(POSSIBLE_SCORES, repeat=len(remaining_games)):
        sim = table[["MP","W","D","L","GF","GA","GD","Pts"]].copy()
        sim_matches = base_group_matches.copy()

        for (team1, team2), (s1, s2) in zip(remaining_games, outcome_set):
            sim_matches.append((group, team1, s1, team2, s2))

            sim.loc[team1, "MP"] += 1
            sim.loc[team2, "MP"] += 1

            sim.loc[team1, "GF"] += s1
            sim.loc[team1, "GA"] += s2
            sim.loc[team2, "GF"] += s2
            sim.loc[team2, "GA"] += s1

            if s1 > s2:
                sim.loc[team1, "W"] += 1
                sim.loc[team2, "L"] += 1
                sim.loc[team1, "Pts"] += 3
            elif s1 < s2:
                sim.loc[team2, "W"] += 1
                sim.loc[team1, "L"] += 1
                sim.loc[team2, "Pts"] += 3
            else:
                sim.loc[team1, "D"] += 1
                sim.loc[team2, "D"] += 1
                sim.loc[team1, "Pts"] += 1
                sim.loc[team2, "Pts"] += 1

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

    end_time = time.time()
    #st.write(f"Scenario loop time: {end_time - start_time:.2f} sec")   
    
    probabilities = {}
    first_probabilities = {}
    statuses = {}

    finished = len(remaining_games) == 0
    if finished:
        final_ranked = rank_with_head_to_head(
            table[["MP","W","D","L","GF","GA","GD","Pts"]].copy(),
            matches,
            group
        )
        final_order = list(final_ranked.index)
    else:
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

def build_group_table(group):
    teams = groups[group]

    table = pd.DataFrame(
        0,
        index=teams,
        columns=["MP", "W", "D", "L", "GF", "GA", "GD", "Pts"]
    )

    for g, team1, score1, team2, score2 in matches:
        if g != group:
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

    table = rank_with_head_to_head(table, matches, group)

    return table

def build_group_matrix(group, ranked):
    matrix = pd.DataFrame("⏳", index=ranked.index, columns=ranked.index)

    for team in ranked.index:
        matrix.loc[team, team] = "—"

    for g, team1, score1, team2, score2 in matches:
        if g != group:
            continue

        matrix.loc[team1, team2] = f"{score1}-{score2}"
        matrix.loc[team2, team1] = f"{score2}-{score1}"

    return matrix


def get_group_data(group):
    ranked = build_group_table(group)
    matrix = build_group_matrix(group, ranked)

    statuses, probabilities, first_probabilities = calculate_group_status_and_probability(
        group,
        ranked,
        matrix
    )

    return ranked, matrix, statuses, probabilities, first_probabilities

def rank_third_placed_teams():
    third_teams = []

    for group in sorted(groups.keys()):
        ranked = build_group_table(group)

        third_team = ranked.index[2]

        third_teams.append({
            "Group": group,
            "Team": third_team,
            "Pts": ranked.loc[third_team, "Pts"],
            "GD": ranked.loc[third_team, "GD"],
            "GF": ranked.loc[third_team, "GF"],
            "Group Status": "Completed" if get_group_remaining_count(group) == 0 else "In Progress",
        })

    third_df = pd.DataFrame(third_teams)

    third_df = third_df.sort_values(
        ["Pts", "GD", "GF"],
        ascending=False
    ).reset_index(drop=True)

    third_df["Third Place Rank"] = range(1, len(third_df) + 1)
    third_df["Advance"] = third_df["Third Place Rank"].apply(
        lambda x: "✅ Advance" if x <= 8 else "❌ Out"
    )

    return third_df

# =====================
# UI Functions
# =====================

def summary_card(label, team, pts, gd, gf, border_color, background_color, badge=None):
    gd_text = f"+{gd}" if gd > 0 else str(gd)

    badge_html = ""
    if badge is not None:
        badge_html = f"""
<hr style="border:none;border-top:1px solid #dddddd;margin:12px 0;">
<div style="
font-size:16px;
font-weight:700;
background:#ffffffcc;
border:1px solid #e5e7eb;
border-radius:999px;
padding:6px 12px;
display:inline-block;
">
{badge}
</div>
"""

    st.markdown(
        f"""
<div style="
background:{background_color};
border:1px solid #e5e7eb;
border-top:8px solid {border_color};
border-radius:16px;
padding:16px;
box-shadow:0 4px 12px rgba(0,0,0,0.06);
min-height:160px;
">
<div style="font-size:14px;color:#6b7280;margin-bottom:8px;">{label}</div>

<div style="
font-size:28px;
font-weight:950;
color:#1f2937;
margin-bottom:14px;
line-height:1.2;
">
{team}
</div>

<div style="
display:grid;
grid-template-columns:repeat(3,1fr);
gap:8px;
margin-top:12px;
">
<div style="text-align:center;">
<div style="font-size:12px;color:#6b7280;font-weight:700;">Pts</div>
<div style="font-size:20px;font-weight:900;color:#1f2937;">{pts}</div>
</div>

<div style="text-align:center;">
<div style="font-size:12px;color:#6b7280;font-weight:700;">GD</div>
<div style="font-size:20px;font-weight:900;color:#1f2937;">{gd_text}</div>
</div>

<div style="text-align:center;">
<div style="font-size:12px;color:#6b7280;font-weight:700;">GF</div>
<div style="font-size:20px;font-weight:900;color:#1f2937;">{gf}</div>
</div>
</div>

{badge_html}

</div>
""",
        unsafe_allow_html=True
    )

def show_group(selected_group):

# =====================
# Group Standings
# =====================

    table = build_group_table(selected_group)
    matrix = build_group_matrix(selected_group, table)
    teams = list(table.index)

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
        st.success(f"🏆Group {selected_group} finished")
    else:
        st.info(f"⚽Group {selected_group}: {remaining_count} matches remaining")

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
        pts = table.loc[team, "Pts"]
        gd = table.loc[team, "GD"]
        gf = table.loc[team, "GF"]
        status = table.loc[team, "Status"]

        with col:
            summary_card(
                label,
                team,
                pts,
                gd,
                gf,
                border_colors[i],
                background_colors[i],
                badge=status
            )

    st.subheader(f"Group {selected_group} Standings")
    standings_df = table.reset_index().rename(columns={"index": "Team"})

    row_colors = [
        "#F5FAFF",  # 1st
        "#F4FCF6",  # 2nd
        "#FFFAF2",  # 3rd
        "#FFF5F5"   # 4th
    ]

    html_parts = []

    html_parts.append('<div style="width:100%; overflow-x:auto;">')
    html_parts.append(
        '<table style="width:100%; border-collapse:separate; border-spacing:0; '
        'border-radius:14px; overflow:hidden; '
        'box-shadow:0 4px 14px rgba(0,0,0,0.08); font-size:14px;">'
    )

    html_parts.append('<thead>')
    html_parts.append('<tr style="background:#1f4e79;color:white;">')

    for col in standings_df.columns:
        html_parts.append(
            f'<th style="padding:12px 10px; text-align:center; font-weight:700; '
            f'border-bottom:3px solid #F4A300; white-space:nowrap;">{col}</th>'
        )

    html_parts.append('</tr>')
    html_parts.append('</thead>')
    html_parts.append('<tbody>')

    for i, row in standings_df.iterrows():
        bg = row_colors[i] if i < len(row_colors) else "#ffffff"
        html_parts.append(f'<tr style="background:{bg};">')

        for col in standings_df.columns:
            value = row[col]

            if col in ["1st Scenario %", "Top 2 Scenario %"]:
                value = f"{value:.1f}"

            weight = "700" if col in ["Team", "Pts", "Status"] else "400"

            html_parts.append(
                f'<td style="padding:12px 10px; text-align:center; '
                f'border-bottom:1px solid #e5e7eb; border-right:1px solid #e5e7eb; '
                f'font-weight:{weight}; white-space:nowrap;">{value}</td>'
            )

        html_parts.append('</tr>')

    html_parts.append('</tbody>')
    html_parts.append('</table>')
    html_parts.append('</div>')

    html = "".join(html_parts)

    st.markdown(html, unsafe_allow_html=True)

    # =====================
    # Matrix + Match List
    # =====================
    col1, col2 = st.columns([1.6, 0.8])

    with col1:
        st.subheader(f"Group {selected_group} Match Matrix")

        matrix_df = matrix.reset_index().rename(columns={"index": "Team"})

        matrix_parts = []

        matrix_parts.append('<div style="width:100%; overflow-x:auto;">')
        matrix_parts.append(
            '<table style="width:100%; border-collapse:separate; border-spacing:0; '
            'border-radius:14px; overflow:hidden; '
            'box-shadow:0 4px 14px rgba(0,0,0,0.06); font-size:14px;">'
        )

        matrix_parts.append('<thead>')
        matrix_parts.append('<tr style="background:#1f4e79;color:white;">')

        for col in matrix_df.columns:
            matrix_parts.append(
                f'<th style="padding:12px 10px; text-align:center; font-weight:700; '
                f'border-bottom:3px solid #F4A300; white-space:nowrap;">{col}</th>'
            )

        matrix_parts.append('</tr></thead><tbody>')

        for i, row in matrix_df.iterrows():
            bg = "#ffffff" if i % 2 == 0 else "#f8fafc"
            matrix_parts.append(f'<tr style="background:{bg};">')

            for col in matrix_df.columns:
                value = row[col]

                if value == "⏳":
                    cell_html = (
                        '<span style="background:#FFF3CD; color:#B45309; '
                        'padding:6px 14px; border-radius:999px; '
                        'font-weight:700;">Upcoming</span>'
                    )
                elif value == "—":
                    cell_html = '<span style="color:#CBD5E1; font-size:18px;">—</span>'
                elif col == "Team":
                    cell_html = f'<b>{value}</b>'
                else:
                    try:
                        s1, s2 = map(int, str(value).split("-"))

                        if s1 > s2:
                            badge_bg = "#E8F6EF"
                            badge_color = "#166534"
                        elif s1 < s2:
                            badge_bg = "#FFF1F2"
                            badge_color = "#991B1B"
                        else:
                            badge_bg = "#FFF7E8"
                            badge_color = "#92400E"

                        cell_html = (
                            f'<span style="'
                            f'background:{badge_bg}; '
                            f'color:{badge_color}; '
                            f'padding:6px 14px; '
                            f'border-radius:999px; '
                            f'font-weight:800; '
                            f'box-shadow:0 2px 6px rgba(0,0,0,.08);'
                            f'">{value}</span>'
                        )

                    except:
                        cell_html = str(value)

                matrix_parts.append(
                    f'<td style="padding:11px 10px; text-align:center; '
                    f'border-bottom:1px solid #e5e7eb; border-right:1px solid #e5e7eb; '
                    f'white-space:nowrap;">{cell_html}</td>'
                )

            matrix_parts.append('</tr>')

        matrix_parts.append('</tbody></table></div>')

        st.markdown("".join(matrix_parts), unsafe_allow_html=True)

    with col2:
        st.subheader("Matches")

        # =====================
        # Played Match Cards
        # =====================
        played_cards = ""

        for g, team1, score1, team2, score2 in matches:
            if g != selected_group:
                continue

            played_cards += f"""<div style="
background:white;
border:1px solid #e5e7eb;
border-radius:14px;
padding:16px;
margin-bottom:12px;
box-shadow:0 2px 8px rgba(0,0,0,.06);
">
<div style="
display:grid;
grid-template-columns:1fr auto 1fr;
align-items:center;
gap:12px;
font-size:15px;
font-weight:700;
">
<span style="text-align:left;">{team1}</span>
<span style="
font-size:20px;
font-weight:800;
color:#1f2937;
background:#EEF7FF;
padding:6px 16px;
border-radius:999px;
">{score1} - {score2}</span>
<span style="text-align:right;">{team2}</span>
</div>
</div>"""

        if not played_cards:
            played_cards = "No played matches yet"

        st.markdown("#### Played Matches")
        st.markdown(played_cards, unsafe_allow_html=True)

        # =====================
        # Upcoming Match Cards
        # =====================
        remaining_cards = ""

        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                t1 = teams[i]
                t2 = teams[j]

                if matrix.loc[t1, t2] == "⏳":
                    remaining_cards += f"""<div style="
background:#FFFBEB;
border:1px solid #FDE68A;
border-radius:14px;
padding:16px;
margin-bottom:12px;
box-shadow:0 2px 8px rgba(0,0,0,.05);
">
<div style="
display:grid;
grid-template-columns:1fr auto 1fr;
align-items:center;
gap:12px;
font-size:15px;
font-weight:700;
">
<span style="text-align:left;">{t1}</span>
<span style="
background:#FFF3CD;
padding:6px 14px;
border-radius:999px;
font-weight:800;
color:#B45309;
">VS</span>
<span style="text-align:right;">{t2}</span>
</div>
</div>"""

        if not remaining_cards:
            remaining_cards = "No remaining matches"

        st.markdown("#### Upcoming Matches")
        st.markdown(remaining_cards, unsafe_allow_html=True)
    # =====================
    # Score Simulator
    # =====================
    st.markdown("### 🎮 Score Simulator")

    remaining_games = []

    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            t1 = teams[i]
            t2 = teams[j]
            if matrix.loc[t1, t2] == "⏳":
                remaining_games.append((t1, t2))

    if len(remaining_games) == 0:
        st.success("No remaining matches to simulate.")
    else:
        with st.form(key=f"sim_form_{selected_group}"):

            sim_scores = []

            for idx, (t1, t2) in enumerate(remaining_games):
                if idx > 0:
                    st.divider()

                c1, c2, c3 = st.columns([1, 0.2, 1])

                with c1:
                    s1 = st.number_input(
                        t1,
                        min_value=0,
                        max_value=20,
                        value=0,
                        step=1,
                        key=f"sim_{selected_group}_{idx}_{t1}"
                    )

                with c2:
                    st.markdown(
                        "<div style='text-align:center;font-size:24px;font-weight:800;margin-top:30px;'>-</div>",
                        unsafe_allow_html=True
                    )

                with c3:
                    s2 = st.number_input(
                        t2,
                        min_value=0,
                        max_value=20,
                        value=0,
                        step=1,
                        key=f"sim_{selected_group}_{idx}_{t2}"
                    )

                sim_scores.append((t1, int(s1), t2, int(s2)))

            run_sim = st.form_submit_button(
                "⚽ Simulate Matches",
                type="primary",
                use_container_width=True
            )

        if run_sim:
            sim_table = table[["MP","W","D","L","GF","GA","GD","Pts"]].copy()
            sim_matches = matches.copy()

            for t1, s1, t2, s2 in sim_scores:
                sim_matches.append((selected_group, t1, s1, t2, s2))

                sim_table.loc[t1, "MP"] += 1
                sim_table.loc[t2, "MP"] += 1

                sim_table.loc[t1, "GF"] += s1
                sim_table.loc[t1, "GA"] += s2
                sim_table.loc[t2, "GF"] += s2
                sim_table.loc[t2, "GA"] += s1

                if s1 > s2:
                    sim_table.loc[t1, "W"] += 1
                    sim_table.loc[t2, "L"] += 1
                    sim_table.loc[t1, "Pts"] += 3
                elif s1 < s2:
                    sim_table.loc[t2, "W"] += 1
                    sim_table.loc[t1, "L"] += 1
                    sim_table.loc[t2, "Pts"] += 3
                else:
                    sim_table.loc[t1, "D"] += 1
                    sim_table.loc[t2, "D"] += 1
                    sim_table.loc[t1, "Pts"] += 1
                    sim_table.loc[t2, "Pts"] += 1

            sim_table["GD"] = sim_table["GF"] - sim_table["GA"]
            sim_table = rank_with_head_to_head(sim_table, sim_matches, selected_group)
            row_colors = [
                "#F5FAFF",
                "#F4FCF6",
                "#FFFAF2",
                "#FFF5F5"
            ]
            border_colors = [
                "#0057B8",
                "#2BA84A",
                "#F4A300",
                "#D7263D"
            ]

            st.markdown("### 🧪 Simulation Result")

            sim_summary_items = [
                ("🥇 Winner", sim_table.index[0]),
                ("🥈 Runner-up", sim_table.index[1]),
                ("🥉 Third Place", sim_table.index[2]),
                ("❌ Eliminated", sim_table.index[3]),
            ]

            sim_cols = st.columns(4)

            for i, (col, (label, team)) in enumerate(zip(sim_cols, sim_summary_items)):
                pts = sim_table.loc[team, "Pts"]
                gd = sim_table.loc[team, "GD"]
                gf = sim_table.loc[team, "GF"]
                gd_text = f"+{gd}" if gd > 0 else str(gd)

                with col:
                    summary_card(
                        label,
                        team,
                        pts,
                        gd,
                        gf,
                        border_colors[i],
                        row_colors[i]
                    )

            st.markdown("### 📊 Simulated Final Standings")

            sim_df = sim_table.reset_index().rename(columns={"index": "Team"})

            
            sim_parts = []

            sim_parts.append('<div style="width:100%; overflow-x:auto;">')
            sim_parts.append(
                '<table style="width:100%; border-collapse:separate; border-spacing:0; '
                'border-radius:14px; overflow:hidden; '
                'box-shadow:0 4px 14px rgba(0,0,0,0.08); font-size:14px;">'
            )

            sim_parts.append('<thead>')
            sim_parts.append('<tr style="background:#1f4e79;color:white;">')

            for col in sim_df.columns:
                sim_parts.append(
                    f'<th style="padding:12px 10px;text-align:center;font-weight:700;'
                    f'border-bottom:3px solid #F4A300;white-space:nowrap;">{col}</th>'
                )

            sim_parts.append('</tr>')
            sim_parts.append('</thead>')
            sim_parts.append('<tbody>')

            for i, row in sim_df.iterrows():
                bg = row_colors[i] if i < len(row_colors) else "#ffffff"
                sim_parts.append(f'<tr style="background:{bg};">')

                for col in sim_df.columns:
                    value = row[col]
                    weight = "800" if col in ["Team", "Pts"] else "400"

                    sim_parts.append(
                        f'<td style="padding:12px 10px;text-align:center;'
                        f'border-bottom:1px solid #e5e7eb;'
                        f'border-right:1px solid #e5e7eb;'
                        f'font-weight:{weight};white-space:nowrap;">{value}</td>'
                    )

                sim_parts.append('</tr>')

            sim_parts.append('</tbody>')
            sim_parts.append('</table>')
            sim_parts.append('</div>')

            st.markdown("".join(sim_parts), unsafe_allow_html=True)
    
    # =====================
    # Top 2 Scenario Chart
    # =====================
    with st.expander("Top 2 Qualification Chance", expanded=False):
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
<div style="display:flex;justify-content:space-between;margin-top:12px;font-size:16px;">
<span><b>{team}</b></span>
<span>{prob:.1f}%</span>
</div>
""",
                    unsafe_allow_html=True
                )

                st.progress(prob / 100)
    
def show_best_third():
    st.header("🌎 Current Best Third-Placed Teams")

    third_df = rank_third_placed_teams()

    html_parts = []

    html_parts.append('<div style="width:100%; overflow-x:auto;">')
    html_parts.append(
        '<table style="width:100%; border-collapse:separate; border-spacing:0; '
        'border-radius:14px; overflow:hidden; '
        'box-shadow:0 4px 14px rgba(0,0,0,0.08); font-size:14px;">'
    )

    html_parts.append('<thead>')
    html_parts.append('<tr style="background:#1f4e79;color:white;">')

    columns = ["Rank", "Group", "Team", "Pts", "GD", "GF", "Group Status", "Current Status"]

    for col in columns:
        html_parts.append(
            f'<th style="padding:12px 10px; text-align:center; font-weight:700; '
            f'border-bottom:3px solid #F4A300; white-space:nowrap;">{col}</th>'
        )

    html_parts.append('</tr>')
    html_parts.append('</thead>')
    html_parts.append('<tbody>')

    for _, row in third_df.iterrows():
        rank = int(row["Third Place Rank"])

        if rank == 1:
            rank_text = "🥇 1"
        elif rank == 2:
            rank_text = "🥈 2"
        elif rank == 3:
            rank_text = "🥉 3"
        else:
            rank_text = str(rank)

        gd = int(row["GD"])
        gd_text = f"+{gd}" if gd > 0 else str(gd)

        is_advance = rank <= 8

        bg = "#F4FCF6" if is_advance else "#FFF5F5"

        status_badge = (
            '<span style="background:#DCFCE7;color:#166534;'
            'padding:6px 14px;border-radius:999px;font-weight:800;">'
            '🟢 Currently In</span>'
            if is_advance else
            '<span style="background:#FEE2E2;color:#991B1B;'
            'padding:6px 14px;border-radius:999px;font-weight:800;">'
            '🔴 Currently Out</span>'
        )
        group_status_badge = (
            '<span style="background:#DCFCE7;color:#166534;'
            'padding:6px 14px;border-radius:999px;font-weight:800;">'
            'Completed</span>'
            if row["Group Status"] == "Completed" else
            '<span style="background:#DBEAFE;color:#1D4ED8;'
            'padding:6px 14px;border-radius:999px;font-weight:800;">'
            'In Progress</span>'
        )

        values = [
            rank_text,
            row["Group"],
            row["Team"],
            row["Pts"],
            gd_text,
            row["GF"],
            group_status_badge,
            status_badge
        ]

        html_parts.append(f'<tr style="background:{bg};">')

        for col_name, value in zip(columns, values):
            weight = "800" if col_name in ["Rank", "Team", "Pts", "Current Status"] else "500"

            html_parts.append(
                f'<td style="padding:12px 10px;text-align:center;'
                f'border-bottom:1px solid #e5e7eb;'
                f'border-right:1px solid #e5e7eb;'
                f'font-weight:{weight};white-space:nowrap;">{value}</td>'
            )

        html_parts.append('</tr>')

    html_parts.append('</tbody>')
    html_parts.append('</table>')
    html_parts.append('</div>')

    st.markdown("".join(html_parts), unsafe_allow_html=True)
    st.caption(
        "Current ranking only. Final third-place qualification may change because some groups are still in progress."
    )

def render_status_table(df, title, theme="green"):
    st.subheader(title)

    if df.empty:
        st.info("No teams to display.")
        return

    header_color = "#1f4e79"
    accent_color = "#F4A300"
    row_bg = "#F4FCF6" if theme == "green" else "#FFF5F5"

    html_parts = []
    html_parts.append('<div style="width:100%; overflow-x:auto;">')
    html_parts.append(
        '<table style="width:100%; border-collapse:separate; border-spacing:0; '
        'border-radius:14px; overflow:hidden; '
        'box-shadow:0 4px 14px rgba(0,0,0,0.08); font-size:14px;">'
    )

    html_parts.append('<thead>')
    html_parts.append(f'<tr style="background:{header_color};color:white;">')

    for col in df.columns:
        html_parts.append(
            f'<th style="padding:12px 10px;text-align:center;font-weight:800;'
            f'border-bottom:3px solid {accent_color};white-space:nowrap;">{col}</th>'
        )

    html_parts.append('</tr></thead><tbody>')

    for _, row in df.iterrows():
        html_parts.append(f'<tr style="background:{row_bg};">')

        for col in df.columns:
            value = row[col]

            if col == "Status" and theme == "green":
                value = (
                    '<span style="background:#DCFCE7;color:#166534;'
                    'padding:6px 14px;border-radius:999px;font-weight:800;">'
                    f'{value}</span>'
                )
            elif col == "Status" and theme == "red":
                value = (
                    '<span style="background:#FEE2E2;color:#991B1B;'
                    'padding:6px 14px;border-radius:999px;font-weight:800;">'
                    f'{value}</span>'
                )

            weight = "800" if col in ["Team", "Status"] else "500"

            html_parts.append(
                f'<td style="padding:12px 10px;text-align:center;'
                f'border-bottom:1px solid #e5e7eb;'
                f'border-right:1px solid #e5e7eb;'
                f'font-weight:{weight};white-space:nowrap;">{value}</td>'
            )

        html_parts.append('</tr>')

    html_parts.append('</tbody></table></div>')

    st.markdown("".join(html_parts), unsafe_allow_html=True)

def get_remaining_matches_for_team(group, team):
    count = 0
    teams = groups[group]

    for opponent in teams:
        if opponent == team:
            continue

        match_key = tuple(sorted([team, opponent]))

        if match_key in match_info and match_info[match_key]["Status"] == "Remaining":
            count += 1

    return count


def quick_team_status_for_knockout(group, ranked):
    first_locked = []
    eliminated = []

    teams = list(ranked.index)

    for team in teams:
        pts = ranked.loc[team, "Pts"]
        remaining = get_remaining_matches_for_team(group, team)
        max_pts = pts + remaining * 3

        other_max_pts = []

        for other in teams:
            if other == team:
                continue

            other_remaining = get_remaining_matches_for_team(group, other)
            other_max_pts.append(ranked.loc[other, "Pts"] + other_remaining * 3)

        # 第一名鎖定：其他所有隊最高分都追不上
        if team == ranked.index[0] and pts > max(other_max_pts):
            first_locked.append({
                "Group": group,
                "Team": team,
                "Status": "🥇 1st Locked"
            })

        # 淘汰：即使全勝，積分也無法進前二
        #higher_or_equal_max = sum(
         #   1 for other in teams
         #   if other != team and ranked.loc[other, "Pts"] >= max_pts
        #)

        #if higher_or_equal_max >= 2:
         #   eliminated.append({
         #       "Group": group,
         #       "Team": team,
         #       "Status": "🔴 Eliminated"
         #   })

    return first_locked, eliminated

def show_tournament():
    st.header("🏆 Knockout Qualification")
    st.caption(
        "Qualified and eliminated teams are listed here based on confirmed tournament status. "
        "Best third-placed teams are added after all groups are completed."
    )

    first_locked = []
    eliminated = []

    all_groups_completed = all(
        get_group_remaining_count(group) == 0
        for group in groups.keys()
    )

    if all_groups_completed:
        st.success(
            "🏁 Group Stage Completed\n\n"
            "All qualification results have been finalized. "
            "Best third-placed teams have also been confirmed."
        )
        accurate_mode = False
    else:
        st.info(
            "**⚡ Fast Analysis**\n\n"
            "Completed groups:\n"
            "• Qualified teams\n"
            "• Eliminated teams\n\n"
            "**🔍 Accurate Analysis**\n\n"
            "Unfinished groups:\n"
            "• Detect mathematically confirmed qualification\n"
            "• Detect mathematically confirmed elimination"
        )
        
        st.markdown(
            "<div style='text-align:center;color:#6b7280;font-size:16px;margin-bottom:8px;'>"
            "Need mathematically confirmed qualification?"
            "</div>",
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns([1,2,1])

        with col2:

            accurate_mode = st.button(
                "🔍 Run Accurate Analysis (≈3 min)",
                type="primary",
                use_container_width=True
            )

        if accurate_mode:
            st.info(
                "🔍 Running accurate qualification analysis...\n\n"
                "Estimated time: ~3 minutes."
            )

    for group in sorted(groups.keys()):
        ranked = build_group_table(group)
        remaining_count = get_group_remaining_count(group)

        if remaining_count == 0:
            first_locked.append({
                "Group": group,
                "Team": ranked.index[0],
                "Status": "🥇 Winner"
            })

            first_locked.append({
                "Group": group,
                "Team": ranked.index[1],
                "Status": "🥈 Runner-up"
            })

            eliminated.append({
                "Group": group,
                "Team": ranked.index[3],
                "Status": "🔴 Eliminated"
            })

        elif accurate_mode and remaining_count <= 2:
            matrix = build_group_matrix(group, ranked)

            with st.spinner(f"Running Group {group}..."):
                statuses, _, _ = calculate_group_status_and_probability(
                    group,
                    ranked,
                    matrix
                )

            for team, status in statuses.items():
                if status in ["🥇 1st Locked", "🥇 Winner"]:
                    first_locked.append({
                        "Group": group,
                        "Team": team,
                        "Status": status
                    })

                elif status in ["🔴 Eliminated", "❌ Fourth Place"]:
                    eliminated.append({
                        "Group": group,
                        "Team": team,
                        "Status": "🔴 Eliminated"
                    })

    if accurate_mode:
        st.success(
            "✅ Accurate qualification analysis completed. "
            "Results now include mathematically confirmed qualification and elimination from unfinished groups."
        )
    

    if all_groups_completed:
        third_df = rank_third_placed_teams()
        qualified_third_df = third_df[third_df["Third Place Rank"] <= 8]

        for _, row in qualified_third_df.iterrows():
            first_locked.append({
                "Group": row["Group"],
                "Team": row["Team"],
                "Status": "🥉 Best Third"
            })

        unqualified_third_df = third_df[
            third_df["Third Place Rank"] > 8
        ]

        for _, row in unqualified_third_df.iterrows():
            eliminated.append({
                "Group": row["Group"],
                "Team": row["Team"],
                "Status": "🔴 Eliminated"
            })
    
    qualified_count = len(first_locked)
    eliminated_count = len(eliminated)
    remaining_count_total = 48 - qualified_count - eliminated_count

    st.markdown("### 📊 Qualification Progress")

    progress_cols = st.columns(3)

    if all_groups_completed:
        progress_items = [
            ("🏆 Qualified for Round of 32", f"{qualified_count} / 32", "Confirmed teams", "#0057B8", "#F5FAFF"),
            ("✅ Tournament Status", "Completed", "Group stage finalized", "#2BA84A", "#F4FCF6"),
            ("🔴 Eliminated", f"{eliminated_count} / 48", "Teams out", "#D7263D", "#FFF5F5"),
    ]
    else:
        progress_items = [
            ("🏆 Qualified for Round of 32", f"{qualified_count} / 32", "Confirmed teams", "#0057B8", "#F5FAFF"),
            ("⏳ Still Alive", f"{remaining_count_total} / 48", "Teams still in contention", "#F4A300", "#FFFAF2"),
            ("🔴 Eliminated", f"{eliminated_count} / 48", "Teams out", "#D7263D", "#FFF5F5"),
        ]

    for col, (label, value, note, border_color, bg_color) in zip(progress_cols, progress_items):
        with col:
            st.markdown(
                f"""
<div style="
background:{bg_color};
border:1px solid #e5e7eb;
border-top:8px solid {border_color};
border-radius:16px;
padding:18px;
box-shadow:0 4px 12px rgba(0,0,0,0.06);
min-height:135px;
">
<div style="font-size:15px;color:#6b7280;font-weight:700;margin-bottom:8px;">{label}</div>
<div style="font-size:34px;font-weight:950;color:#1f2937;line-height:1.2;">{value}</div>
<div style="font-size:14px;color:#6b7280;margin-top:10px;">{note}</div>
</div>
""",
                unsafe_allow_html=True
            )

    if all_groups_completed:
        st.markdown("#### ✅ Round of 32 Qualification Complete")
        st.progress(1.0)
        st.caption("All qualified teams have been confirmed.")

    else:
        st.markdown("#### 🏁 Road to Round of 32")
        st.progress(qualified_count / 32)
        st.caption(f"{qualified_count} / 32 teams have qualified for the Round of 32.")
    
    col1, col2 = st.columns(2)

    with col1:
        render_status_table(
            pd.DataFrame(first_locked),
            "🏆 Qualified Teams",
            theme="green"
        )

    with col2:
        render_status_table(
            pd.DataFrame(eliminated),
            "🔴 Eliminated Teams",
            theme="red"
        )
        
    if all_groups_completed:
        st.markdown("---")

        with st.expander(
            f"⚽ Round of 32 · {completed_matches}/16 Completed",
            expanded=True
        ):
            round32_matches = [
                ("Match 1", "South Africa", "Canada"),
                ("Match 2", "Brazil", "Japan"),
                ("Match 3", "Germany", "Paraguay"),
                ("Match 4", "Netherlands", "Morocco"),
                ("Match 5", "Ivory Coast", "Norway"),
                ("Match 6", "France", "Sweden"),
                ("Match 7", "Mexico", "Ecuador"),
                ("Match 8", "England", "DR Congo"),
                ("Match 9", "Belgium", "Senegal"),
                ("Match 10", "United States", "Bosnia and Herzegovina"),
                ("Match 11", "Spain", "Austria"),
                ("Match 12", "Portugal", "Croatia"),
                ("Match 13", "Switzerland", "Algeria"),
                ("Match 14", "Australia", "Egypt"),
                ("Match 15", "Argentina", "Cape Verde"),
                ("Match 16", "Colombia", "Ghana"),
            ]

            match_cols = st.columns(4)

            for idx, (match_no, team1, team2) in enumerate(round32_matches):
                with match_cols[idx % 4]:
                    st.markdown(
                        f"""
<div style="
background:white;
border:1px solid #e5e7eb;
border-radius:16px;
padding:16px;
margin-bottom:16px;
box-shadow:0 3px 10px rgba(0,0,0,0.06);
min-height:150px;
">
<div style="font-size:13px;color:#6b7280;font-weight:800;margin-bottom:12px;">
⚽ {match_no}
</div>

<div style="font-size:18px;font-weight:900;color:#1f2937;line-height:1.5;">
{team1}
</div>

<div style="
text-align:center;
font-size:14px;
font-weight:900;
color:#B45309;
background:#FFF7E8;
border-radius:999px;
padding:5px 12px;
margin:12px 0;
">
VS
</div>

<div style="font-size:18px;font-weight:900;color:#1f2937;line-height:1.5;">
{team2}
</div>
</div>
""",
                        unsafe_allow_html=True
                    )



if view == "🌍 Group Stage":
    show_group(selected_group)

elif view == "🥉 Best Third-Placed Teams":
    show_best_third()

elif view == "🏆 Knockout Stage":
    show_tournament()

