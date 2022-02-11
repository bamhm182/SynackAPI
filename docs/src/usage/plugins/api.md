# Api

The Api Plugin is used to interact DIRECTLY with the Synack API.
It is the last stop before our code touches Synack.

<!-- toc -->

## api.login(method, path, **kwargs)

> This function is used to set up requests sent to `https://login.synack.com/api/*`.\
> This function takes in several arguments to build information that is sent to `api.request()`.
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `method` | str | HTTP Method (GET, POST, etc.)
> | `path` | str | The full or partial URL to use with the Login API
> | `**kwargs` | kwargs | Passed through to `api.request()`. Look there for more info
>
>> Examples
>> ```python3
>> >>> headers = {
>> ...     "X-CSRF-Token": "123"
>> ... }
>> >>> data = {
>> ...     "email": "some@guy.com",
>> ...     "password": "password1234"
>> ... }
>> >>> h.api.login('POST', 'authenticate', headers=headers, data=data)
>> <class 'requests.models.Response'>
>> ```

## api.notifications(method, path, **kwargs)

> This function is used to set up requests sent to `https://notifications.synack.com/api/v2/*`.\
> This function takes in several arguments to build information that is sent to `api.request()`.
> 
> | Arguments | Type | Description
> | --- | --- | ---
> | `method` | str | HTTP Method (GET, POST, etc.)
> | `path` | str | The full or partial URL to use with the Login API
> | `**kwargs` | kwargs | Passed through to `api.request()`. Look there for more info
>
>> Examples
>> ```python3
>> >>> h.api.notifications('GET', 'notifications?meta=1')
>> <class 'requests.models.Response'>
>> ```

## api.request(method, path, **kwargs)

> This function is used to set up requests sent to the primary API at `https://platform.synack.com/api/*`.\
> 
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `method` | str | HTTP Method (GET, POST, etc.)
> | `path` | str | The full or partial URL to use with the Login API
> | `kwargs['headers']` | dict | Headers that should be applied to only the current request
> | `kwargs['query']` | dict | Query parameters that should be added onto the URL
> | `kwargs['data']` | dict | Data parameters that should be used in the Body
> | 
>
>> Examples
>> ```python3
>> >>> query = {
>> ...     "status": "PUBLISHED",
>> ...     "viewed": "false"
>> ... }
>> >>> h.api.request('HEAD', 'tasks/v1/tasks', query=query)
>> <class 'requests.models.Response'>
>> ```
