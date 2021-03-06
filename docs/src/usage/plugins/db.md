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
| ips | Yes | No | All cached IPs
| notifications_token | No | No | Synack Notifications Token used to authenticate requests
| otp_secret | No | Yes | Synack OTP Secret
| password | No | Yes | The password used to log into Synack
| ports | Yes | No | All cached Ports
| proxies | Yes | Yes | A dict built from http_proxy and https_proxy
| scratchspace_dir | No | Yes | The path to a directory where your working files (scopes, scans, etc.) are stored
| slack_url | No | Yes | The Slack API URL used for Notifications
| smtp_email_from | No | Yes | Email Source for SMTP Notifications
| smtp_email_to | No | Yes | Email Destination for SMTP Notifications
| smtp_password | No | Yes | Password to use for SMTP Server Auth
| smtp_port | No | Yes | Port of SMTP Server (Ex: 465)
| smtp_server | No | Yes | URL of SMTP Server (Ex: smtp.gmail.com)
| smtp_starttls | No | Yes | Boolean to determine whether TLS is used for SMTP
| smtp_username | No | Yes | Username to use for SMTP Server Auth
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

## db.add_ips(results, session=None)

> Add IP Addresses to the database
>
> | Argument | Type | Description
> | --- | --- | ---
> | `results` | list(dict) | A list of dictionaries containing `ip` addresses and `target` slugs
> | `session` | sqlalchemy.orm.sessionmaker() | A database session. This function is often used with `db.add_ports()` and can have a session passed into it
>
>> Examples
>> ```python3
>> >>> h.db.add_ips([{'ip': '1.1.1.1', 'target': '230h94ei'}, ...])
>> ```

## db.add_organizations(targets, session)

> Add Organizations from the Synack API to the Database
>
> | Argument | Type | Description
> | --- | --- | ---
> | `targets` | list | A list of Target dictionaries returned from the Synack API
> | `session` | sqlalchemy.orm.sessionmaker() | A database session. This function is most often used with `db.add_targets()` and I was having issues getting it to work when it would create a new session
>
>> Examples
>> ```python3
>> >>> h.db.add_organizations([{...}, {...}, {...}])
>> ```

## db.add_ports(results)

> Add port results to the database
> 
> | Arguments | Type | Description
> | --- | --- | ---
> | `results` | list(dict) | A list of dictionaries containing results from some scan, Hydra, etc.
>
>> Examples
>> ```python3
>> >>> results = [
>> ...     {
>> ...         "ip": "1.1.1.1",
>> ...         "target": "7gh33tjf72",
>> ...         "source": "nmap",
>> ...         "ports": [
>> ...             {
>> ...                 "port": "443",
>> ...                 "protocol": "tcp",
>> ...                 "service": "Super Apache NGINX Deluxe",
>> ...                 "screenshot_url": "http://127.0.0.1/h3298h23.png",
>> ...                 "url": "http://bubba.net",
>> ...                 "open": True,
>> ...                 "updated": 1654969137
>> ...
>> ...             },
>> ...             {
>> ...                 "port": "53",
>> ...                 "protocol": "udp",
>> ...                 "service": "DNS"
>> ...             }
>> ...         ]
>> ...     }
>> ... ]
>> >>> h.db.add_ports(results)
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

## db.add_urls(results)

> Add urls results to the database
> 
> | Arguments | Type | Description
> | --- | --- | ---
> | `results` | list(dict) | A list of dictionaries containing results from some scan, Hydra, etc.
>
>> Examples
>> ```python3
>> >>> results = [
>> ...     {
>> ...         "ip": "1.1.1.1",
>> ...         "target": "7gh33tjf72",
>> ...         "urls": [
>> ...             {
>> ...                 "url": "https://www.google.com",
>> ...                 "screenshot_url": "https://imgur.com/2uregtu",
>> ...             },
>> ...             {
>> ...                 "url": "https://www.ebay.com",
>> ...                 "screenshot_url": "file:///tmp/948grt.png",
>> ...             }
>> ...         ]
>> ...     }
>> ... ]
>> >>> h.db.add_urls(results)
>> ```

## db.find_ips(ip, **kwargs)

> Filters through all the ips to return ones which match a given criteria
>
> | Argument | Type | Description
> | --- | --- | ---
> | `ip` | str | IP Address to search for
> | `kwargs` | kwargs | Any attribute of the Target Database Model (codename, slug, is_active, etc.)
>
>> Examples
>> ```python3
>> >>> h.db.find_ips(codename="SLEEPYPUPPY")
>> [{'ip': '1.1.1.1, 'target': '12398h21'}, ... ]
>> ```

## db.find_ports(port, protocol, source, ip, **kwargs)

> Filters through all the ports to return ones which match a given criteria
>
> | Argument | Type | Description
> | --- | --- | ---
> | `port` | int | Port number to search for (443, 80, 25, etc.)
> | `protocol` | str | Protocol to search for (tcp, udp, etc.)
> | `source` | str | Source to search for (hydra, nmap, etc.)
> | `ip` | str | IP Address to search for
> | `kwargs` | kwargs | Any attribute of the Target Database Model (codename, slug, is_active, etc.)
>
>> Examples
>> ```python3
>> >>> h.db.find_ports(codename="SLEEPYPUPPY")
>> [
>>   {
>>     'ip': '1.2.3.4', 'source': 'hydra', 'target': '123hg912',
>>       'ports': [
>>         { 'open': True, 'port': '443', 'protocol': 'tcp', 'service': 'https - Wordpress', 'updated': 1654840021 },
>>         ...
>>       ]
>>   },
>>   ...
>> ]
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

## db.find_urls(url=None, ip=None, **kwargs)

> Filters through all the ports to return ones which match a given criteria
>
> | Argument | Type | Description
> | --- | --- | ---
> | `url` | str | Url hosting a service on the IP
> | `ip` | str | IP Address to search for
> | `kwargs` | kwargs | Any attribute of the Target Database Model (codename, slug, is_active, etc.)
>
>> Examples
>> ```python3
>> >>> h.db.find_ports(codename="SLEEPYPUPPY")
>> [
>>   {
>>     'ip': '1.2.3.4',
>>     'target': '123hg912',
>>     'ports': [
>>       {  
>>         'url': 'https://www.google.com',
>>         'screenshot_url': 'file:///tmp/2948geybu24.png'
>>       },
>>       ...
>>     ]
>>   },
>>   ...
>> ]
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
