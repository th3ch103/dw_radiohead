{{ config(materialized='table') }}

select
    upper(trim(trackname))              as track_name,
    upper(trim(artistname))             as artist_name,
    trim(collectionname)                as album_name,
    trim(primarygenrename)              as genre,
    tracktimemillis                     as track_time_ms,
    to_date(releasedate)                as release_date,
    extract(year from to_date(releasedate)) as release_year
from MALLARD_PROJECT.PUBLIC.ITUNES_RADIOHEAD_RAW
