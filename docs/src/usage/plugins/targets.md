# Targets

## targets.build_codename_from_slug(slug)

> Returns a Target's codename given its slug.
>
> This hits the local database, then hits the Synack API if it can't find it.
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `slug` | str | The slug of a Target
>
>> Examples
>> ```python3
>> >>> h.targets.build_codename_from_slug('uwfpmfpgjlum')
>> 'DAPPERDINGO'
>> ```

## targets.build_scope_host_db(slug, scope)

> Prints a list of IPs ready to ingest into the Database
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `slug` | str | The slug of a Target
> | `scope` | list(dict) | Return of `targets.get_scope_host()` from Synack's API
>
>> Examples
>> ```python3
>> >>> scope = h.targets.get_scope(codename='JANGLYJALOPY')
>> >>> scope_db = h.targets.build_scope_host_db(scope)
>> >>> scope_db
>> [
>>   {'ip': '1.1.1.1', 'target': '2398her8h'},
>>   ...
>> ]
>> >>> h.db.add_ips(scope_db)
>> ```

## targets.build_scope_web_burp(scope)

> Prints a dictionary compatible with Burp Suite from the output of `targets.get_scope_web()`
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `scope` | list(dict) | Return of `targets.get_scope_web()` from Synack's API
>
>> Examples
>> ```python3
>> >>> scope = h.targets.get_scope(codename='SLAPPYMONKEY')
>> >>> h.targets.build_scope_web_burp(scope)
>> {'target': {'scope': {
>>     'advanced_mode': 'true',
>>     'exclude': [{'enabled': True, 'scheme': 'https', 'host': 'bad.monkey.com', 'file': '/'}, ...]
>>     'include': [{'enabled': True, 'scheme': 'https', 'host': 'good.monkey.com', 'file': '/'}, ...]
>> }}}
>> ```

## targets.build_scope_web_db(scope)

> Prints a list of URLs which can be ingested into the Database
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `scope` | list(dict) | Return of `targets.get_scope_web()` from Synack's API
>
>> Examples
>> ```python3
>> >>> scope = h.targets.get_scope(codename='SLAPPYMONKEY')
>> >>> scope_db = h.targets.build_scope_web_db(scope)
>> >>> scope_db
>> [
>>   {
>>     'target': '94hw8ier',
>>     'urls': [{'url': 'https://good.monkey.com'}]
>>   },
>>   ...
>> ]
>> >>> h.db.add_urls(scope_db)
>> ```

## targets.build_scope_web_urls(scope)

> Prints a dictionary containing lists of `in` scope and `out` of scope URLs
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `scope` | list(dict) | Return of `targets.get_scope_web()` from Synack's API
>
>> Examples
>> ```python3
>> >>> scope = h.targets.get_scope(codename'SLAPPYMONKEY')
>> >>> h.targets.build_scope_web_urls(scope)
>> {'in': ['good.monkey.com'], 'out': ['bad.monkey.com']}
>> ```

## targets.build_slug_from_codename(codename)

> Returns a Target's slug given its codename.
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `codename` | str | The codename of a Target
>
>> Examples
>> ```python3
>> >>> h.targets.build_slug_from_codename('DAPPERDINGO')
>> 'uwfpmfpgjlum'
>> ```

## targets.get_assessments()

> Pull back a list of assessments and whether you have passed them.
>
> This function caches your status in the Database and will affect certain queries like `targets.get_unregistered()`, which will only pull back targets in categories you have passed.
>
>> Examples
>> ```python3
>> >>> h.targets.get_assessments()
>> [{"id": 1, ...},...]
>> ```

## targets.get_assets(self, target=None, asset_type=None, host_type=None, active='true', scope=['in', 'discovered'], sort='location', sort_dir='asc', page=None, organization_uid=None, **kwargs)

> Pull back a list of assets related to a target.
>
> If no arguments are provided, whatever target you are currently connected to will be queried with the default paramters.
> You can use the following arguments to specify a target/organization or override default parameters.
>
> Note that `scopeRules` and `listings` both have a `scope` field, which is confusing.
> From the best I can tell, the one in `listings` is the one that matters.
> PLEASE double check my math before trusting it blindly and let me know if I'm wrong.
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `target` | db.models.Target | A single Target returned from the database
> | `asset_type` | str | Type of target ('host', 'webapp', etc.)
> | `host_type` | str | Type of information to get back ('cidr')
> | `active` | str | This field appears to specify whether the asset is an active item in the target's scope
> | `scope` | str | I'm honestly not entirely sure what this field is, but the default is ['in', 'discovered'] when made officially.
> | `sort_dir` | str | SQL-type sort direction (`asc`, `desc`)
> | `page` | int | The page of assets to return
> | `organization_uid` | str | slug of the organization that owns the target
>
>> Examples
>> ```python3
>> >>> h.targets.get_assets()
>> [{
>> 'listings': [{'listingUid': 'iuqwehuh4', 'scope': 'in'}, ...],
>> 'location': 'https://www.something.com (https://www.something.com)',
>> 'scopeRules': [{'appliesTo': 'both', 'rule': '*.www.something.com/*', 'uid': 'qiuwe'}, ...],
>> ...
>> }, ...]

## targets.get_attachments(target, **kwargs)

> Gets the attachments of a specific target.
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `target` | db.models.Target | A single Target returned from the database
> | `kwargs` | kwargs | Information used to look up a Target in the database (ex: `codename`, `slug`, etc.)
>
>> Examples
>> ```python3
>> >>> h.targets.get_attachments(codename='SLAPPYFROG')
>> [{
>>   'id': 1337, 'listing_id': '7sl4ppyfr0g', 'created_at': 1659461184, 'updated_at': 1659712248,
>>   'filename': 'FrogApp.apk', 'url': 'https://storage.googleapis.com/...' 
>> }, ...]

## targets.get_connected()

> Return minimal information about your currently connected Target
>
>> Examples
>> ```python3
>> >>> h.targets.get_connected()
>> {"slug": "ulmpupflgm", "codename": "GOOFYGOPHER", "status": "Connected"}
>> ```

## targets.get_connections(target, **kwargs)

> Get the connection details of a target
>
> | Argments | Type | Description
> | --- | --- | ---
> | `target` | db.models.Target | A single Target returned from the database
> | `kwargs` | kwargs | Information used to look up a Target in the database (ex: `codename`, `slug`, etc.)
>
>> Examples
>> ```python3
>> >>> h.targets.get_connections(codename='BLINKYBABOON')
>> {"lifetime_connections":200,"current_connections":0}
>> ```

## targets.get_credentials(**kwargs)

> Pulls back the credentials for a Target
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `kwargs` | kwargs | Some attribute that will be used to identify a Target
>
>> Examples
>> ```python3
>> >>> h.targets.get_credentials(slug='ljufpbgylu')
>> [{"credentials": [{...},...],...}]
>> >>> h.targets.get_credentials(codename='CHILLINCHILLA')
>> [{"credentials": [{...},...],...}]
>> ```

## targets.get_query(status='registered', query_changes={})

> Pulls back a list of targets matching the specified query
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `status` | string | The type of targets to pull back. (Ex: `registered`, `unregistered`, `upcoming`, `all`)
> | `query_changes` | dict() | Changes to make to the standard query. (Ex: `{"sorting['field']": "dateUploaded"}`
>
>> Examples
>> ```python3
>> >>> h.targets.get_query(status='unregistered')
>> [{"codename": "SLEEPYSLUG", ...}, ...]
>> ```

## targets.get_registered_summary()

> The Registered Summary is a short list of information about every target you have registered.
> The endpoint used by this function is hit every time you refresh a page on the platform, so
> eventhough it sounds like a lot, it isn't bad.
>
> Information from this function is cached in the Database
>
>> Examples
>> ```python3
>> >>> h.targets.get_unregistered_summary()
>> {"pflupm": {"id": "pflupm",...},...}
>> ```

## targets.get_scope(**kwargs)

> Returns scope information for web or host targets when given target identifiers.
> If no kwargs are provided, the scope of your currently connected target will be retrieved.
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `kwargs` | kwargs | Information used to look up a Target in the database (ex: `codename`, `slug`, etc.)
>
>> Examples
>> ```python3
>> >>> h.targets.get_scope(codename='SILLYFILLY')
>> ['1.1.1.1/32', '10.0.0.0/8', ...]
>> ```

## targets.get_scope_host(target, **kwargs)

> Return CIDR IP Addresses in scope when given a Target or target identifiers
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `target` | db.models.Target | A single Target returned from the database
> | `kwargs` | kwargs | Information used to look up a Target in the database (ex: `codename`, `slug`, etc.)
>
>> Examples
>> ```python3
>> >>> tgt = h.db.find_targets(codename='SILLYFILLY')
>> >>> h.targets.get_scope_host(tgt)
>> ['1.1.1.1/32', '10.0.0.0/8', ...]
>> >>> h.targets.get_scope_host(slug='92wg38itur')
>> ['9,9,9,9/32', ...]
>> ```

## targets.get_scope_web(target, **kwargs)

> Returns a ton of information about a web target's scope given a Target or target identifiers
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `target` | db.models.Target | A single Target returned from the database
> | `kwargs` | kwargs | Information used to look up a Target in the database (ex: `codename`, `slug`, etc.)
>
>> Examples
>> ```python3
>> >>> h.targets.get_scope_web(codename='SLAPPYFROG')
>> [{
>>   'raw_url': 'https://good.frog.com', 'status': 'in', 'bandwidth': 0, 'notes': '',
>>   'owners': [{'owner_uid': '97g8ehri', 'owner_type_id': 1, 'codename': 'slappyfrog'}, ...]
>> }, ...]

## targets.get_submissions(target, status="accepted", **kwargs)

> Get the details of previously submitted vulnerabilities from the analytics of a target
>
> | Argments | Type | Description
> | --- | --- | ---
> | `target` | db.models.Target | A single Target returned from the database
> | `status` | str | Query either `accepted`, `rejected` or `in_queue` vulnerabilities
> | `kwargs` | kwargs | Information used to look up a Target in the database (ex: `codename`, `slug`, etc.)
>
>> Examples
>> ```python3
>> >>> h.targets.get_submissions(codename='BLINKYBABOON')
>> [
>>    {
>>      "categories": ["Authorization/Permissions","SSRF"],
>>      "exploitable_locations":[
>>        {"type":"url","value":"https://example.com/index.html","created_at":1625646235,"status":"fixed"},
>>        ...
>>      ]
>>    }, ...
>> ]
>> >>>
>> >>> h.targets.get_submissions(status="in_queue", codename='BLINKYBABOON')
>> [
>>    {
>>      "categories": ["Authorization/Permissions","SSRF"],
>>      "exploitable_locations":[
>>        {"type":"url","value":"https://example.com/login.html","created_at":1625646235,"status":"pending"},
>>        ...
>>      ]
>>    }, ...
>> ]
>> ```

## targets.get_submissions_summary(target, hours_ago=None, **kwargs)

> Get a summary of the submission analytics of a target
>
> | Argments | Type | Description
> | --- | --- | ---
> | `target` | db.models.Target | A single Target returned from the database
> | `hours_ago` | int | The amount of hours since the current time to query the analytics for. (ex: `hours_ago=48` will query how many submissions were made in the last `48` hours. Defaults to lifetime when not set.)
> | `kwargs` | kwargs | Information used to look up a Target in the database (ex: `codename`, `slug`, etc.)
>
>> Examples
>> ```python3
>> >>> h.targets.get_submissions_summary(codename='BLINKYBABOON')
>> 35
>> >>> 
>> >>> h.targets.get_submissions_summary(hours_ago=48, codename='BLINKYBABOON')
>> 5
>> ```

## targets.get_unregistered()

> Gets a list of unregistered Targets from the Synack API.
>
> Only Targets in Categories you have passed will be returned.
>
>> Examples
>> ```python3
>> >>> h.targets.get_unregistered()
>> [{"slug": "lfjpgmk",...},...]
>> ```

## targets.get_upcoming()

> Gets a list of upcoming Targets from the Synack API.
>
>> Examples
>> ```python3
>> >>> h.targets.get_upcoming()
>> [{'codename': 'SLEEPYSLUG', 'upcoming_start_date': 1668430800, ...}, ...]
>> ```

## targets.set_connected(target, **kwargs)

> Connect to a specified target
>
> | Argments | Type | Description
> | --- | --- | ---
> | `target` | db.models.Target | A single Target returned from the database
> | `kwargs` | kwargs | Information used to look up a Target in the database (ex: `codename`, `slug`, etc.)
>
>> Examples
>> ```python3
>> h.targets.set_connected(codename='BLINKYBABOON')
>> >>> {'slug': '12083y9', 'codename': 'BLINKYBABOON', 'status': 'Connected'}
>> h.targets.set_connected(slug='12083y9')
>> >>> {'slug': '12083y9', 'codename': 'BLINKYBABOON', 'status': 'Connected'}
>> ```

## targets.set_registered(targets)

> Registers unregistered Targets.
>
> If no `targets` are provided, `targets.get_unregistered()` is used so that all unregistered targets are registered.
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `targets` | list(dict) | A list of targets returned from the Synack API
>
>> Examples
>> ```python3
>> >>> msns = h.targets.get_unregistered()
>> >>> h.targets.set_unregistered([msns[0]])
>> [{"id": "jlgbmjpbgm",...}]
>> >>>
>> >>> h.targets.set_unregistered()
>> [{"id": "pwjlgmf",...},...]
>> ```
