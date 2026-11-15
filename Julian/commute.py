"""
ENG 220 Team 17 - Commuting in Cuba, NM
Shows one graph: share of commuters by broad commute-time group,
Cuba, NM vs. the United States (same as the MATLAB graph on the slides).

Uses only packages that come with Streamlit (pandas + altair), so no
extra requirements are needed.

Needs, next to this file:
    data/Commute Time.csv

Run locally:   streamlit run commute.py
"""

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

DATA_FILE = Path(__file__).parent / "data" / "Commute Time.csv"

st.set_page_config(page_title="Commutes in Cuba, NM vs. the US")
st.title("Commutes in Cuba, NM in comparison with the US")

if not DATA_FILE.exists():
    st.error("Missing file: put 'Commute Time.csv' in a 'data' folder next to this file.")
    st.stop()

# ---- Load data -----------------------------------------------------------
T = pd.read_csv(DATA_FILE)
T.columns = ["TimeID", "TravelTime", "Year", "Commuters", "MOE",
             "Place", "PlaceID", "Share"]
yr = int(T["Year"].max())                 # most recent year
T = T[T["Year"] == yr]
places = T["Place"].unique().tolist()     # "United States", "Cuba, NM"

# ---- Combine the 12 travel-time ranges into 5 broad groups ---------------
group_labels = ["Under 15 min", "15-29 min", "30-44 min", "45-59 min", "60+ min"]
group_of = {0: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 1, 6: 2, 7: 2, 8: 2, 9: 3, 10: 4, 11: 4}
T = T.assign(Group=T["TimeID"].map(group_of).map(lambda g: group_labels[g]))
df = (T.groupby(["Group", "Place"], as_index=False)["Share"].sum())
df["SharePct"] = (100 * df["Share"]).round(1)
df["Label"] = df["SharePct"].map(lambda v: f"{v:.1f}%")

# ---- Plot (MATLAB-style dark theme, MATLAB default colors) ---------------
colors = ["#0072BD", "#D95319"]           # MATLAB blue and orange
ymax = (int(df["SharePct"].max() // 10) + 1) * 10 + 5

base = alt.Chart(df).encode(
    x=alt.X("Group:N", sort=group_labels, title=None, axis=alt.Axis(labelAngle=0)),
    xOffset=alt.XOffset("Place:N", sort=places),
    y=alt.Y("SharePct:Q", title="Share of Commuters (%)",
            scale=alt.Scale(domain=[0, ymax])),
    color=alt.Color("Place:N", sort=places,
                    scale=alt.Scale(domain=places, range=colors[:len(places)]),
                    legend=alt.Legend(title=None, orient="top-right")),
)
bars = base.mark_bar(stroke="white", strokeWidth=0.5)
labels = base.mark_text(dy=-7, color="white", fontSize=11).encode(text="Label:N")

chart = (
    (bars + labels)
    .properties(title=f"Commute Time, {yr}", height=420, background="black")
    .configure_view(fill="black", stroke="white")
    .configure_axis(labelColor="white", titleColor="white", gridColor="#444444",
                    domainColor="white", tickColor="white", labelFontSize=12)
    .configure_title(color="white", fontSize=16)
    .configure_legend(labelColor="white", fillColor="black", strokeColor="white",
                      padding=6, labelFontSize=12)
)

st.altair_chart(chart, use_container_width=True, theme=None)

st.caption(f"Source: Data USA, \"Cuba, NM,\" {yr} ACS data.")
