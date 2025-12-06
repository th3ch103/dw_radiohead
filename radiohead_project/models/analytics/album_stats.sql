{{ config(materialized='table') }}

-- Album-level statistics for Radiohead tracks

select
    album_name,
    count(*)           as track_count,
    avg(track_time_ms) as avg_track_length_ms,
    min(track_time_ms) as min_track_length_ms,
    max(track_time_ms) as max_track_length_ms,
    min(release_date)  as first_release_date,
    max(release_date)  as last_release_date
from {{ ref('stg_radiohead') }}
group by album_name