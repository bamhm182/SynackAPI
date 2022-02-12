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

## targets.get_connected()

> Return minimal information about your currently connected Target
>
>> Examples
>> ```python3
>> >>> h.get_connected()
>> {"slug": "ulmpupflgm", "codename": "GOOFYGOPHER", "status": "Connected"}
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
