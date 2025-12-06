import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd

# Get Snowflake session
session = get_active_session()

# ---- Page config ----
st.set_page_config(
    page_title="Radiohead Mini DW",
    page_icon="🎵",
    layout="wide",
)

st.title("🎵 Radiohead Mini Data Warehouse")

st.caption(
    "Built on three layers: RAW (`ITUNES_RADIOHEAD_RAW`) → STAGING (`STG_RADIOHEAD`) "
    "→ ANALYTICS (`ALBUM_STATS`, `YEAR_STATS`)."
)

# ---- Data loading ----
@st.cache_data
def load_data():
    """Load analytics and staging tables from Snowflake."""
    album_df = session.table("ALBUM_STATS").to_pandas()
    year_df = session.table("YEAR_STATS").to_pandas()
    stg_df = session.table("STG_RADIOHEAD").to_pandas()

    # Normalize column names to lower snake_case
    album_df.columns = [c.lower() for c in album_df.columns]
    year_df.columns = [c.lower() for c in year_df.columns]
    stg_df.columns = [c.lower() for c in stg_df.columns]

    # Convert durations to minutes for readability
    if "track_time_ms" in stg_df.columns:
        stg_df["track_seconds"] = stg_df["track_time_ms"] / 1000.0
        stg_df["track_minutes"] = stg_df["track_time_ms"] / 60000.0

    if "avg_track_length_ms" in album_df.columns:
        album_df["avg_length_min"] = album_df["avg_track_length_ms"] / 60000.0

    if "avg_length_ms" in year_df.columns:
        year_df["avg_length_min"] = year_df["avg_length_ms"] / 60000.0

    # Ensure release_year is numeric
    if "release_year" in stg_df.columns:
        stg_df["release_year"] = pd.to_numeric(stg_df["release_year"], errors="coerce")
    if "release_year" in year_df.columns:
        year_df["release_year"] = pd.to_numeric(year_df["release_year"], errors="coerce")

    return album_df, year_df, stg_df


album_df, year_df, stg_df = load_data()

# ---- Sidebar filters ----
st.sidebar.header("Filters")

# Year range filter based on staging table
if not stg_df.empty and "release_year" in stg_df.columns:
    min_year = int(stg_df["release_year"].min())
    max_year = int(stg_df["release_year"].max())
    year_range = st.sidebar.slider(
        "Release year range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1,
    )
else:
    year_range = (None, None)

# Album filter (multiselect)
album_options = sorted(stg_df["album_name"].dropna().unique().tolist())
selected_albums = st.sidebar.multiselect(
    "Albums (optional)",
    options=album_options,
    default=[],
)

# Apply filters to staging data
filtered_stg = stg_df.copy()

if year_range[0] is not None:
    filtered_stg = filtered_stg[
        (filtered_stg["release_year"] >= year_range[0])
        & (filtered_stg["release_year"] <= year_range[1])
    ]

if selected_albums:
    filtered_stg = filtered_stg[filtered_stg["album_name"].isin(selected_albums)]

# Recompute filtered album/year views
filtered_album = (
    filtered_stg.groupby("album_name", as_index=False)
    .agg(
        track_count=("track_name", "count"),
        avg_track_length_ms=("track_time_ms", "mean"),
    )
)
if not filtered_album.empty:
    filtered_album["avg_length_min"] = filtered_album["avg_track_length_ms"] / 60000.0

filtered_year = (
    filtered_stg.groupby("release_year", as_index=False)
    .agg(
        tracks_released=("track_name", "count"),
        avg_length_ms=("track_time_ms", "mean"),
    )
)
if not filtered_year.empty:
    filtered_year["avg_length_min"] = filtered_year["avg_length_ms"] / 60000.0


# ---- Overview KPIs ----
total_tracks = len(filtered_stg)
unique_albums = filtered_stg["album_name"].nunique()
avg_length_min_overall = (
    filtered_stg["track_minutes"].mean() if "track_minutes" in filtered_stg.columns else None
)

kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
kpi_col1.metric("Total tracks (filtered)", total_tracks)
kpi_col2.metric("Unique albums (filtered)", unique_albums)
if avg_length_min_overall is not None:
    kpi_col3.metric(
        "Avg track length (min)",
        f"{avg_length_min_overall:.2f}",
    )
else:
    kpi_col3.metric("Avg track length (min)", "N/A")


# ---- Tabs ----
tab_overview, tab_albums, tab_tracks = st.tabs(
    ["📈 Overview", "💿 By Album", "🎧 Tracks Explorer"]
)


# === Tab 1: Overview ===
with tab_overview:
    st.subheader("Tracks Released per Year")

    if not filtered_year.empty:
        st.dataframe(filtered_year[["release_year", "tracks_released"]].sort_values("release_year"))
        st.line_chart(
            filtered_year.set_index("release_year")[["tracks_released"]],
            height=300,
        )
    else:
        st.info("No data available for the selected filters.")

    st.subheader("Average Track Length by Year (minutes)")
    if not filtered_year.empty:
        st.area_chart(
            filtered_year.set_index("release_year")[["avg_length_min"]],
            height=300,
        )
    else:
        st.info("No data available for yearly average length.")


# === Tab 2: By Album ===
with tab_albums:
    st.subheader("Album-level Statistics")

    if not filtered_album.empty:
        display_album = filtered_album.sort_values("avg_length_min", ascending=False)
        st.dataframe(
            display_album[
                ["album_name", "track_count", "avg_length_min"]
            ].rename(
                columns={
                    "album_name": "Album",
                    "track_count": "Tracks",
                    "avg_length_min": "Avg length (min)",
                }
            )
        )

        st.bar_chart(
            display_album.set_index("album_name")[["avg_length_min"]],
            height=350,
        )
    else:
        st.info("No album stats for the selected filters.")

    st.markdown("### Pick an album to inspect its tracks")

    if album_options:
        # Default selection: first album or user-selected
        default_album = selected_albums[0] if selected_albums else album_options[0]
        album_choice = st.selectbox("Album", options=album_options, index=album_options.index(default_album))

        album_tracks = filtered_stg[filtered_stg["album_name"] == album_choice].copy()
        if not album_tracks.empty:
            album_tracks = album_tracks.sort_values("track_minutes", ascending=False)
            st.dataframe(
                album_tracks[
                    ["track_name", "track_minutes", "release_date", "genre"]
                ].rename(
                    columns={
                        "track_name": "Track",
                        "track_minutes": "Length (min)",
                        "release_date": "Release date",
                        "genre": "Genre",
                    }
                )
            )
        else:
            st.info("No tracks for this album with current filters.")


# === Tab 3: Tracks Explorer ===
with tab_tracks:
    st.subheader("Tracks Explorer")

    if filtered_stg.empty:
        st.info("No tracks to display for the current filters.")
    else:
        # Controls
        col_left, col_right = st.columns(2)
        with col_left:
            top_n = st.slider("How many tracks to show?", min_value=5, max_value=30, value=10, step=1)
        with col_right:
            mode = st.radio(
                "Sort by",
                options=["Longest tracks", "Shortest tracks"],
                horizontal=True,
            )

        df_tracks = filtered_stg.copy()

        if mode == "Longest tracks":
            df_tracks = df_tracks.sort_values("track_minutes", ascending=False)
        else:
            df_tracks = df_tracks.sort_values("track_minutes", ascending=True)

        df_tracks = df_tracks.head(top_n)

        st.dataframe(
            df_tracks[
                ["track_name", "album_name", "track_minutes", "release_year", "genre"]
            ].rename(
                columns={
                    "track_name": "Track",
                    "album_name": "Album",
                    "track_minutes": "Length (min)",
                    "release_year": "Year",
                    "genre": "Genre",
                }
            )
        )

st.markdown("---")
st.caption("Built with Snowflake + dbt + Streamlit · Filters apply to all tabs.")
