{#
  prod: models land in their custom schema as-is (staging, analytics).
  other targets: prefixed with the target schema (dbt_dev_staging, dbt_dev_analytics)
  so development never touches the tables Power BI reads.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- elif target.name == 'prod' -%}
        {{ custom_schema_name | trim }}
    {%- else -%}
        {{ target.schema }}_{{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
