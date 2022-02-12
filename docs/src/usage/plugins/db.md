# Db

This plugin deals with interacting with the database.

This plugin is a little different in most in that it has a couple functions which deal with database queries, in addition to many properties.
Some properties are Read-Only, while others can be Set.
Additionally, some properties can be overridden by the State, which allows you to change the way one Handler instance runs without affecting others.

| Property | Read-Only | State Override | Description
| --- | --- | --- | ---
| api_token | No | No | Synack Access Token used to authenticate requests
| categories | Yes | No | All cached Categories
| debug | No | Yes | Changes the verbosity of some actions, such as network requests
| email | No | Yes | The email used to log into Synack
| http_proxy | No | Yes | The http web proxy (Burp, etc.) to use for requests
| https_proxy | No | Yes | The https web proxy (Burp, etc.) to use for requests
| notifications_token | No | No | Synack Notifications Token used to authenticate requests
| otp_secret | No | Yes | Synack OTP Secret
| password | No | Yes | The password used to log into Synack
| proxies | Yes | Yes | A dict built from http_proxy and https_proxy
| targets | Yes | No | All cached Targets
| template_dir | No | Yes | The path to a directory where your templates are stored
| use_proxies | No | Yes | Changes whether or not http_proxy and https_proxies are used
| user_id | No | No | Your Synack User ID used for requests

## db.add_categories(categories)

> Add Target Categories from the Synack API to the Database
> This is most often used with the `targets.get_assessments()` function so that you are only returned information about Categories you have access to.
>
> | Argument | Type | Description
> | --- | --- | ---
> | `categories` | list | A list of Category dictionaries returned from the Synack API
>
>> Examples
>> ```python3
>> >>> h.db.add_categories([{...}, {...}, {...}])
>> ```

## db.add_organizations(targets, session)

> Add Organizations from the Synack API to the Database
>
> | Argument | Type | Description
> | --- | --- | ---
> | `targets` | list | A list of Target dictionaries returned from the Synack API
> | `session` | sqlalchemy.orm.sessionmaker() | A database section. This function is most often used with add_targets and I was having issues getting it to work when it would create a new session
>
>> Examples
>> ```python3
>> >>> h.db.add_organizations([{...}, {...}, {...}])
>> ```

## db.add_targets(targets)

> Adds Target from the Synack API to the Database
>
> | Argument | Type | Description
> | --- | --- | ---
> | targets | list(dict) | A list of Target dictionaties returned from the Synack API
>
>> Examples
>> ```python3
>> >>> h.db.add_targets([{...}, {...}, {...}])
>> ```

## db.find_targets(**kwargs)

> Filters through all the targets to return ones which match a given criteria
>
> | Argument | Type | Description
> | --- | --- | ---
> | `kwargs` | kwargs | Any attribute of the Target Database Model (codename, slug, is_active, etc.)
>
>> Examples
>> ```python3
>> >>> h.db.find_targets(codename="SLEEPYPUPPY")
>> [<class 'synack.db.models.Target'>, ...]
>> ```

## db.get_config(name)

> Returns a configuration from the Database.
>
> | Argument | Type | Description
> | --- | --- | ---
> | `name` | str | The desired config to pull. If none provided, the entire config object will return.
>
>> Examples
>> ```python3
>> >>> h.db.get_config('api_token')
>> 'reuif...oetuhhj'
>> >>> g.db.get_config('user_id')
>> 'heutih9'
>> ```

## db.remove_targets(**kwargs)

> Remove targets from the Database based on criteria.
> **If no criteria is provided, all entries are deleted**
>
> | Argument | Type | Description
> | --- | --- | ---
> | `kwargs` | kwargs | Criteria by which to find Targets for deletion (codename, slug, etc.)
>
>> Examples
>> ```python3
>> >>> h.db.remove_targets(codename='SLUGISHPARROT')
>> ```

## db.set_config(name, value)

> Permanently sets a configuration in the Database
>
> | Argument | Type | Description
> | --- | --- | ---
> | `name` | str | Name of the config to set
> | `value` | ? | Value to set the config to
>
>> Examples
>> ```python3
>> >>> h.db.set_config('email', '1@2.com')
>> >>> h.db.set_config('password', 'password1234')
>> ```

## db.set_migration()

> Migrates the local database to include the newest changes.
> This may need to be run manually when SynackAPI is updated until I can figure out a better way to have it run automatically.
>
>> Examples
>> ```python3
>> >>> h.db.set_migration()
>> ```
