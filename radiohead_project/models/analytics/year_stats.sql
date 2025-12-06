{{ config(materialized='table') }}

-- Year-level statistics for Radiohead tracks

select
    release_year,
    count(*)           as tracks_released,
    avg(track_time_ms) as avg_length_ms
from {{ ref('stg_radiohead') }}
group by release_year
order by release_year
