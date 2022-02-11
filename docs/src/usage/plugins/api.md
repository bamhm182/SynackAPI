# Api

The Api Plugin is used to interact DIRECTLY with the Synack API.
It is the last stop before our code touches Synack.

## api.login(method, path, **kwargs)

> This function is used to set up requests sent to `https://login.synack.com/api/*`.\
> This function takes in several arguments to build information that is sent to `api.request()`.
>
> | Arguments | Description
> | --- | ---
> | `method` | HTTP Method (GET, POST, etc.)
> | `path` | The full or partial URL to use with the Login API
> | `**kwargs` | Passed through to `api.request()`. Look there for more info
>
>> Examples
>> ```python3
>> h.api.login('POST', 'authenticate', headers=headers, data=data)
>> ```


## api.notifications(method, path, **kwargs)

> DESCRIPTION
>
> | Arguments | Description
> | --- | ---
> | `1` | one
>
>> Examples
>> ```python3
>> h.
>> ```


## api.request(method, path, **kwargs)

> DESCRIPTION
>
> | Arguments | Description
> | --- | ---
> | `1` | one
>
>> Examples
>> ```python3
>> h.
>> ```
