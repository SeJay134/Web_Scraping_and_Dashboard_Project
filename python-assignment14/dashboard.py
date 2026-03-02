# 4. Dashboard Program

import streamlit as st
import plotly.express as px
import sqlite3
import pandas as pd

# Setup
st.set_page_config(
    page_title="YEAR-BY-YEAR MLB HISTORY",
    page_icon="⚾",
    layout="wide"
)

# Connect to db
conn = sqlite3.connect("db/mlb_history.db", check_same_thread=False)
db = pd.read_sql("SELECT * FROM main_data_american_league", conn)
conn.close()

# Checking
print("--info--")
db.info()

print(db.dtypes)
print()

print("--describe--\n", db.describe())
print()
for col in db:
    print("--describe--\n", db[col].describe().tail(2))

print("--nan--")
print(db.isna().sum())
print()

print('--duplicated--\n', db.duplicated().sum())

print("Unique years")
print(sorted(db['year'].unique()))
print()

db_copy = db.copy()

# Title
st.title("⚾ The History of Major League Baseball")
st.markdown("Interactive dashboard for analyzing MLB")

# Table
st.markdown(
f"""
<div style="display:flex; justify-content: space-between; width:100%;">
    <div style="text-align:center; flex:1; padding:10px; border:1px solid #ddd; border-radius:5px;">
        <div style="font-size:24px; font-weight:bold;">{len(db_copy)}</div>
        <div>⚾ Total Records</div>
    </div>
    <div style="text-align:center; flex:1; padding:10px; border:1px solid #ddd; border-radius:5px;">
        <div style="font-size:24px; font-weight:bold;">{db_copy["name"].nunique()}</div>
        <div>👤 Unique Players</div>
    </div>
    <div style="text-align:center; flex:1; padding:10px; border:1px solid #ddd; border-radius:5px;">
        <div style="font-size:24px; font-weight:bold;">{db_copy["team"].nunique()}</div>
        <div>🏟 Total Teams</div>
    </div>
    <div style="text-align:center; flex:1; padding:10px; border:1px solid #ddd; border-radius:5px;">
        <div style="font-size:24px; font-weight:bold;">{db_copy['year'].min()} - {db_copy['year'].max()}</div>
        <div>📅 Years Covered</div>
    </div>
    <div style="text-align:center; flex:1; padding:10px; border:1px solid #ddd; border-radius:5px;">
        <div style="font-size:24px; font-weight:bold;">{db_copy['year'].nunique()}</div>
        <div>🏆 Total Seasons</div>
    </div>
</div>
""",
unsafe_allow_html=True
)

# Sidebar filtres
st.sidebar.title("Filters")

# year
years = sorted(db_copy["year"].unique())
default_year_index = years.index(1901)

with st.sidebar.expander("Year selection", expanded=True):
    selected_year = st.selectbox("Select year", options=years, index=default_year_index)

df_filtered_year = db_copy[db_copy["year"] == selected_year]

# player - name

names = sorted(df_filtered_year["name"].unique())

# setup
default_name_index = 0
if "Nap Lajoie" in names:
    default_name_index = names.index("Nap Lajoie")

with st.sidebar.expander("Name selection", expanded=True):
    selected_name = st.selectbox("Select name", options=names, index=default_name_index)

df_filtered = db_copy[(db_copy["year"] == selected_year) & (db_copy['name'] == selected_name)]

df_group_stats = (df_filtered.groupby('statistic', as_index=False)['value'].sum().sort_values("value", ascending=False))

# Plot 1
# one player
fig_one_player = px.bar(
    df_group_stats,
    x="statistic",
    y="value",
    orientation='v',
    title=f"{selected_name} - {selected_year} Season stats"
)
fig_one_player.update_traces(width=0.4)
st.plotly_chart(fig_one_player, use_container_width=True)

# Plot 2 Top 10 Players in Selected Year
top_players = (
    db_copy[db_copy["year"] == selected_year]
    .groupby("name", as_index=False)["value"]
    .sum()
    .sort_values("value", ascending=False)
    .head(10)
)

fig_top_players = px.bar(
    top_players,
    x="name",
    y="value",
    title=f"Top 10 Players in {selected_year}"
)

st.plotly_chart(fig_top_players, use_container_width=True)

# Plot 3 Top N Players (dinamic)
st.subheader("Top N Players")

top_n = st.slider("Select Top N Players", 5, 20, 10)

top_n_players = (
    db_copy.groupby("name", as_index=False)["value"]
    .sum()
    .sort_values("value", ascending=False)
    .head(top_n)
)

fig_top_n = px.bar(
    top_n_players,
    x="name",
    y="value",
    title=f"Top {top_n} Players (All Time)"
)

st.plotly_chart(fig_top_n, use_container_width=True)