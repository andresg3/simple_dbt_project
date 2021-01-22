{{
    config(
        materialized="table",
        tags=[
            "arrivals",
        ]
    )
}}

with base_airports as (

    select * from {{ ref('base_airports') }}

),

base_arrivals__ecuador as (

    select * from {{ ref('base_arrivals__ecuador') }}

),

latest_arrival_date as (

    select max(arrival_date) as arrival_date from base_arrivals__ecuador

),

aggregate as (

    select
        arrival_date,
        arrival_iata,
        arrival_icao,
        arrival_airport_name,
        count(*) as flight_count

    from
        base_arrivals__ecuador

    where
        is_code_share is null

    {{ group_by(4) }}

    order by 5 desc

),

final as (

    select
        a.airport_id                as airport_id,
        a."name"                    as "name",
        a.latitude                  as latitude,
        a.longitude                 as longitude,
        coalesce(b.flight_count, 0) as "flight_count"

    from
        base_airports a

        left join
            aggregate b
        on
           a.iata = b.arrival_iata

    where
        a.country = 'Ecuador'
    and
        b.arrival_date in (
            select arrival_date from latest_arrival_date
        )

)

select * from final