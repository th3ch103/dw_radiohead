CREATE OR REPLACE TABLE MALLARD_PROJECT.PUBLIC.ANALYTICS_ALBUM_STATS AS
SELECT
    album_name,
    COUNT(*) AS track_count,
    AVG(track_time_ms) AS avg_track_length_ms,
    MIN(track_time_ms) AS shortest_track_ms,
    MAX(track_time_ms) AS longest_track_ms,
    MIN(release_date) AS first_release,
    MAX(release_date) AS last_release
FROM MALLARD_PROJECT.PUBLIC.STG_RADIOHEAD_TRACKS
GROUP BY album_name
ORDER BY album_name;


CREATE OR REPLACE TABLE MALLARD_PROJECT.PUBLIC.ANALYTICS_YEAR_STATS AS
SELECT
    release_year,
    COUNT(*) AS tracks_released,
    AVG(track_time_ms) AS avg_length_ms
FROM MALLARD_PROJECT.PUBLIC.STG_RADIOHEAD_TRACKS
GROUP BY release_year
ORDER BY release_year;
