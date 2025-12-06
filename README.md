# Radiohead Mini Data Warehouse

A small ELT pipeline built with **Snowflake + dbt + Streamlit** using a curated dataset of Radiohead tracks.

## 1. Extract
Data was collected using the iTunes Search API and saved as: `data/itunes_radiohead_raw.csv`.

Columns include track name, artist, album, genre, duration (ms), and release date.

## 2. Load (Snowflake)
The CSV was uploaded into: `MALLARD_PROJECT.PUBLIC.ITUNES_RADIOHEAD_RAW`.

This is the raw layer.

## 3. Transform (dbt)

### Staging model (`stg_radiohead`)
Cleans and standardizes fields; derives `release_year`. 

Output: `PUBLIC.STG_RADIOHEAD`

### Analytics models
- `album_stats`: track count + avg/min/max duration per album  
- `year_stats`: tracks released + avg duration per year  

Outputs:
- `PUBLIC.ALBUM_STATS`
- `PUBLIC.YEAR_STATS`


## 4. Dashboard (Streamlit in Snowflake)
An interactive Streamlit app was built using Snowpark.

Features:
- Filters (year range, album)
- KPIs (track count, album count, avg length)
- Charts:
  - Tracks released per year
  - Avg track length per album
- Track explorer (longest/shortest tracks)

## 5. Project Structure
```
dw_radiohead/
data/
radiohead_project/ (dbt project)
models/
staging/
analytics/
```


## 6. Summary
This project demonstrates a full ELT workflow:
**Extract → Load → Transform (dbt) → Visualize (Streamlit)**.