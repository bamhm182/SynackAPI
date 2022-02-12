# Templates

## templates.build_filepath(mission)

> Builds a safe filepath for the template to exist at
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `mission` | dict | A mission dict returned from the Synack API
>
>> Examples
>> ```python3
>> >>> msn = {
>> ...     "taskType": "SV2M",
>> ...     "assetTypes": ["host"],
>> ...     "title": "More Realistic Name: CVE-1970-1"
>> ... }
>> >>> h.templates.build_filepath(msn)
>> '/home/user/Templates/sv2m/host/more_realistic_name_cve_1970_1.txt'
>> >>> msn = {
>> ...     "taskType": "MISSION",
>> ...     "assetTypes": ["web"],
>> ...     "title": "SoME  HoRR!bl3 M!$$!0N"
>> ... }
>> >>> h.templates.build_filepath(msn)
>> '/home/user/Templates/mission/web/some_horr_bl3_m_0n.txt'
>> ```

## templates.build_safe_name(name)

> Takes a name and converts it into something that is definitely safe for a filepath 
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `name` | str | Some string to convert into a standardized string that if definitely safe to use as a filepath
>
>> Examples
>> ```python3
>> >>> h.build_safe_name('R@ND0M     G@RB@G3!!!!!')
>> 'r_nd0m_g_rb_ge_'
>> ```

## templates.build_sections(path)

> Take the text from a local template file and prepare it to be sent to the Synack API
>
> | Arguments | Description
> | --- | ---
> | `path` | pathlib.PosixPath | Path to the template file that should be uploaded
>
>> Examples
>> ```python3
>> >>> h.templates.build_sections(Path('/home/user/Templates/mission/web/mission.txt'))
>> {
>>    "introduction": "This is the intro",
>>    "testing_methodology": "This is how I tested",
>>    "conclusion": "This is the conclusion",
>>    "structuredResponse": "no"
>> }
>> ```

## templates.get_file(mission)

> Pulls in a local template file to upload to a given mission
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `mission` | dict | A mission dict from the Synack API
>
>> Examples
>> ```python3
>> >>> msns = h.missions.get_claimed()
>> >>> h.templates.get_file(msns[0])
>> {"introduction": "This is the intro",...}
>> ```

## templates.set_file(evidences)

> Writes evidences pulled from `missions.get_evidences()` to a local template file
>
> Note that if the file already exists, it will not be overwritten
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `evidences` | dict | Evidences from `missions.get_evidences()`
>
>> Examples
>> ```python3
>> >>> msns = h.missions.get_approved()
>> >>> evidences = h.missions.get_evidences(msns[0])
>> >>> h.templates.set_file(evidences)
>> '/home/user/Templates/mission/web/some_new_mission.txt'
>> ```
