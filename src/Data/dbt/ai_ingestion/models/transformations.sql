{{ config(materialized='table') }}

WITH source_data AS (

    SELECT
        1 as id
        ,'value1' as column1
        
    UNION ALL

    SELECT
        null as id
        ,null as column1

)

,cleaned_data AS (
    SELECT
        id,
        TRIM(REPLACE(column1, '\n', ' ')) AS column1
    FROM
    source_data
)
  
,non_nulls AS (
    SELECT 
        *
    FROM
        cleaned_data
    WHERE 
        column1 IS NOT NULL
)

,
unique_rows AS (
    SELECT 
        DISTINCT *
    FROM
        non_nulls
)

SELECT 
*
FROM
    unique_rows
