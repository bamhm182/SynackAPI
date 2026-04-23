# Duo

## duo.get_duo_push_values(code)

> Registers SynackAPI as a virtual Duo device using an activation code from the Duo admin portal.
> Stores the resulting credentials (`akey`, `pkey`, `host`) in the database for use in subsequent
> logins. This only needs to be run once.
>
> | Arguments | Description
> | --- | ---
> | `code` | Duo activation code in the format `<code>-<base64host>` (from the Duo admin QR code)
>
>> Examples
>> ```python3
>> >>> h.duo.get_duo_push_values('ABCDEF-dGVzdC5kdW9zZWN1cml0eS5jb20=')
>> ```

## duo.get_grant_token(auth_url)

> Handles Duo Security MFA stages and returns the grant_token used to finish logging into Synack
>
> | Arguments | Description
> | --- | ---
> | `auth_url` | Duo Security Authentication URL generaated by sending credentials to Synack
>
>> Examples
>> ```python3
>> >>> h.duo.get_grant_token('https:///...duosecurity.com/...')
>> 'Y8....6g'
>> ```

## duo.set_duo_push_approved()

> Fetches pending Duo push transactions for the registered virtual device and approves them.
> Called automatically during login when `duo_akey` is set in the database.
>
>> Examples
>> ```python3
>> >>> h.duo.set_duo_push_approved()
>> ```
