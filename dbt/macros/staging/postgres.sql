
{% macro index(this, column) %}

    create index if not exists "{{ this.name }}__index_on_{{ column }}" on {{ this }} ("{{ column }}")
    -- create index if not exists "base_airports__index_on_country" on "postgres"."analysis"."base_airports" ("country")

{% endmacro %}


{% macro group_by(n) %}

  GROUP BY
   {% for i in range(1, n + 1) %}
     {{ i }}
     {% if not loop.last %} , {% endif %}
   {% endfor %}

{% endmacro %}