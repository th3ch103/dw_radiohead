-- Create a clean staging table for Radiohead track data.
-- This layer standardizes column names, parses dates, and removes bad whitespace.

CREATE OR REPLACE TABLE MALLARD_PROJECT.PUBLIC.STG_RADIOHEAD_TRACKS AS
SELECT
    UPPER(TRIM(trackname))        AS track_name,        -- clean song name
    UPPER(TRIM(artistname))       AS artist_name,       -- standardize artist
    TRIM(collectionname)          AS album_name,        -- album / collection
    TRIM(primarygenrename)        AS genre,             -- genre
    tracktimemillis               AS track_time_ms,     -- duration in ms
    releasedate                   AS release_timestamp, -- already TIMESTAMP
    TO_DATE(releasedate)          AS release_date,      -- date only
    YEAR(releasedate)             AS release_year       -- extract year
FROM MALLARD_PROJECT.PUBLIC.ITUNES_RADIOHEAD_RAW;


SELECT * 
FROM MALLARD_PROJECT.PUBLIC.STG_RADIOHEAD_TRACKS
LIMIT 10;