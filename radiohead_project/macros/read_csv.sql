{% macro read_csv(path) %}
    {{
        external_source(
            path=path,
            file_format={
                "type": "csv",
                "field_delimiter": ",",
                "skip_header": 1
            }
        )
    }}
{% endmacro %}
