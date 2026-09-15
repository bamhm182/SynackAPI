# Auth

This plugin deals with authenticating the user to Synack.

## auth.get_api_token()

> Walks through the whole authentication workflow to get a new api_token
>
>> Examples
>> ```python3
>> >>> h.auth.get_api_token()
>> '489hr98hf...eh59'
>> ```

## auth.get_authentication_response(csrf)

> Send the username and password to Synack and returns the response
>
> | Arguments | Description
> | --- | ---
> | `csrf` | CSRF token issued by Synack Authentication Workflow
>
>> Examples
>> ```python3
>> >>> csrf = h.auth.get_login_csrf()
>> >>> h.auth.get_authentication_response(csrf)
>> {'success': True, ..., 'duo_auth_url': 'https://...'}
>> ```

## auth.get_login_csrf()

> Pulls a CSRF Token from the Login page
>
>> Examples
>> ```python3
>> >>> h.auth.get_login_csrf()
>> '45h998h4g5...45wh89g9wh'
>> ```

## auth.get_notifications_token()

> Walks through the whole process of getting a notifications token
>
>> Examples
>> ```python3
>> >>> h.auth.get_notifications_token()
>> '958htiu...h98f5ht'
>> ```

## auth.set_api_token_invalid()

> Invalidates the API Token by logging out
>
>> Examples
>> ```python3
>> >>> h.auth.set_api_token_invalid()
>> ```

## auth.set_login_script()

> Writes the current api_token to `~/.config/synack/login.js` JavaScript file to help with staying logged in.
>
>> Examples
>> ```python3
>> >>> auth.set_login_script()
>> ```
