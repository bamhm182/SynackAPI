# Hydra

## hydra.build_db_input()

> Builds a list of ports ready to be ingested by the Database from Hydra output
>
>> Examples
>> ```python3
>> >>> h.hydra.build_db_input(h.hydra.get_hydra(codename='SLEEPYPUPPY', update_db=False))
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

## hydra.get_hydra(page, max_page, update_db, **kwargs)

> Returns information from Synack Hydra Service
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `page` | int | Page of the Hydra Service to start on (Default: 1)
> | `max_page` | int | Highest page that should be queried (Default: 5)
> | `update_db` | bool | Store the results in the database
>
>> Examples
>> ```python3
>> >>> h.hydra.get_hydra(codename='SLEEPYPUPPY')
>> [{'host_plugins': {}, 'ip': '1.2.3.4', 'last_changed_dt': '2022-01-01T01:02:03Z', ... }, ... ]
>> >>> h.hydra.get_hydra(codename='SLEEPYPUPPY', page=3, max_page=5, update_db=False)
>> [{'host_plugins': {}, 'ip': '3.4.5.6', 'last_changed_dt': '2022-01-01T01:02:03Z', ... }, ... ]
>> ```
