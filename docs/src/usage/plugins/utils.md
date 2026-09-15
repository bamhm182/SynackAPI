# Utils

## utils.get_html_tag_value(field, text)

> Looks for an HTML tag in raw HTML and returns its value
>
> | Arguments | Description
> | --- | ---
> | `field` | name of HTML field to find value for
> | `text` | raw HTML content
>
>> Examples
>> ```python3
>> >>> html = '...<input type="hidden" name="tacos" value="tasty"/>...'
>> >>> h.utils.get_html_tag_value('tacos', html)
>> 'tasty'
>> ```
