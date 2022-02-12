# Auth

This plugin deals with authenticating the user to Synack.

## auth.build_otp()

> Use your stored otp_secret to generate a current OTP code
>
>> Examples
>> ```python3
>> >>> h.auth.build_otp()
>> '1234567'
>> ```

## auth.get_api_token()

> Walks through the whole authentication workflow to get a new api_token
>
>> Examples
>> ```python3
>> >>> h.auth.get_api_token()
>> '489hr98hf...eh59'
>> ```

## auth.get_login_csrf()

> Pulls a CSRF Token from the Login page
>
>> Examples
>> ```python3
>> >>> h.auth.get_login_csrf()
>> '45h998h4g5...45wh89g9wh'
>> ```

## auth.get_login_grant_token(csrf, progress_token)

> Get a Login Grant Token by providing an OTP Code
>
> | Argument | Type | Description
> | --- | --- | ---
> | `csrf` | str | A CSRF Token used while logging in
> | `progress_token` | str | A token returned after submitting a valid username and password
>
>> Examples
>> ```python3
>> >>> csrf = h.auth.get_login_csrf()
>> >>> lpt = h.auth.get_login_progress_token(csrf)
>> >>> h.auth.get_login_grant_token(csrf, lpt)
>> '58t7i...rh87g58'
>> ```

## auth.get_login_progress_token(csrf)

> Get the Login Progress Token by authenticating with email and password
>
> | Argument | Type | Description
> | --- | --- | ---
> | `csrf` | str | A CSRF Token used while logging in
>
>> Examples
>> ```python3
>> >>> csrf = h.auth.get_login_csrf()
>> >>> h.auth.get_login_progress_token(csrf)
>> '239rge7...8tehtyg'
>> ```

## auth.get_notifications_token()

> Walks through the whole process of getting a notifications token
>
>> Examples
>> ```python3
>> >>> h.auth.get_notifications_token()
>> '958htiu...h98f5ht'
>> ```

## auth.set_login_script()

> Writes the current api_token to `~/.config/synack/login.js` JavaScript file to help with staying logged in.
>
>> Examples
>> ```python3
>> >>> auth.set_login_script()
>> ```
