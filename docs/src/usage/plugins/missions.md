# Missions

## missions.build_order(missions, sort)

> Takes in a list of missions and returns them sorted in a particular way
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `missions` | list(dict) | A list of missions pulled from the SynackAPI
> | `sort` | srt | The way the missions should be sorted</br>(Default: "payout-high")</br>(Options: "payout-high", "payout-low", "shuffle", "reverse")
>
>> Examples
>> ```python3
>> >>> msns = [{"title": "Some mission",...}, {"title": "Another mission",...}]
>> >>> h.missions.build_order(msns, "reverse")
>> [{"title": "Another mission",...}, {"title": "Some mission",...}]
>> ```

## missions.build_summary(missions)

> Takes a list of missions and summarizes them
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `missions` | list(dict) | A list of missions returned from the Synack API
>
>> Examples
>> ```python3
>> >>> h.missions.build_summary(h.missions.get_claimed())
>> {"count": 5, "value": 250, "time": 86158}
>> ```

## missions.get(status, max_pages, page, per_page, listing_uids)

> Get a list of missions from the Synack API
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `status` | str | Status of missions to claim</br>(Default: "PUBLISHED")
> | `max_pages` | int | The maximum number of pages to grab</br>(Default: 1)
> | `page` | int | The page you wish to start on</br>(Default: 1)
> | `per_page` | int | The number of missions you wish to return per page</br>(Default: 20)
> | `listing_uids` | str | The slug of a specific Target to query for missions</br>(Default: None)
>
> The default `per_page` on the Synack API is 20.
> I recommend leaving it there unless you also plan to try and get multiple pages of missions if there are more than 20.
> Don't set this number TOO high, or you may be requesting a lot of data, which may actually be detremental to the speed of your bot and the Synack API.
> Also consider that if there are multiple pages, you may just be better off still requesting 20 missions, but starting with the second page.
>
> In other words, when using this function, please consider what you are asking the computers to do.
>
>> Examples
>> ```python3
>> >>> h.missions.get()
>> [{"status": "PUBLISHED", "title": "Some Mission",...},...]
>> ```

## missions.get_approved()

> Get one page (Up to 20 missions) from the missions you have previously had approved
>
>> Examples
>> ```python3
>> >>> h.missions.get_approved()
>> [{"status": "APPROVED", "title": "Some Mission",...},...]
>> ```

## missions.get_available()

> Get one page (Up to 20 missions) from the missions currently available for claiming
>
>> Examples
>> ```python3
>> >>> h.missions.get_available()
>> [{"status": "PUBLISHED", "title": "Some Mission",...},...]
>> ```

## missions.get_claimed()

> Get one page (Up to 20 missions) from the missions you currently have
>
>> Examples
>> ```python3
>> >>> h.missions.get_claimed()
>> [{"status": "CLAIMED", "title": "Some Mission",...},...]
>> ```

## missions.get_count(status, listing_uids)

> Get the number of missions
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `status` | str | Status of missions to claim</br>(Default: "PUBLISHED")
> | `listing_uids` | str | The slug of a specific Target to query</br>(Default: None)
>
>> Examples
>> ```python3
>> >>> h.missions.get_count()
>> 10
>> ```

## missions.get_evidences(mission)

> Download the text part of a mission
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `mission` | dict | Mission dict pulled from the Synack API
>
>> Examples
>> ```python3
>> >>> msns = h.missions.get_approved()
>> >>> h.missions.get_evidences(msns[0])
>> {"title": "Some Mission", "asset": "Web", "type": "MISSION",
>>     "structuredResponese": "no", "introduction": "This is the intro",
>>     "testing_methodology": "This is the testing methodology section",
>>     "conclusion": "This is the conclusion section"}
>> ```

## missions.get_in_review()

> Get a list of missions (Up to 20) which are currently being reviewed
>
>> Examples
>> ```python3
>> >>> h.missions.get_in_review()
>> [{"status": "FOR_REVIEW", "title": "Some Mission",...},...]
>> ```

## missions.set_claimed(mission)

> Try and claim one mission
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `mission` | dict | A single mission dict returned from the Synack API
>
>> Examples
>> ```python3
>> >>> msns = h.missions.get_available()
>> >>> h.missions.set_claimed(msns[0])
>> {'target': 'jwfplgu', 'title': 'Some Mission', 'payout': 50,
>>     'status': 'CLAIMED', 'success': True}
>> ```

## missions.set_disclaimed(mission)

> Release one mission you currently have
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `mission` | dict | A single mission dict returned from the Synack API
>
>> Examples
>> ```python3
>> >>> msns = h.missions.get_claimed()
>> >>> h.missions.set_disclaimed(msns[0])
>> {'target': 'jwfplgu', 'title': 'Some Mission', 'payout': 50,
>>     'status': 'DISCLAIMED', 'success': True}
>> ```

## missions.set_evidences(mission)

> Set the evidences (text body) of a mission.
>
> Note that there are protections in place to ensure you don't accidentally nuke a report you are writing.
> These protections currently include confirming that the current fields of the mission have 20 or less characters.
> If you have a lot of text in a mission and wish to replace it with a template, replace all of the text with a single character and try again.
>
> Also note that the templates are pulled from your local file templates.
> Check out the [Mission Templates](../examples/mission-templates.md) page for more information.
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `mission` | dict | A single mission dict returned from the Synack API
>
>> Examples
>> ```python3
>> >>> msns = h.missions.get_claimed()
>> >>> h.missions.set_evidences(msns[0])
>> {'evidenceId': 'uuid4...', 'title': 'Some Mission', 'codename': 'SLEEPYPUPPY'}
>> ```

## missions.set_status(mission, status)

> Sets the status of a mission. Used in `mission.set_claimed` and `missions.set_disclaimed`.
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `mission` | dict | A single mission dict returned from the SynackAPI
> | `status` | str | Status to set it to (i.e., `CLAIM`, `DISCLAIM`)
>
>> Examples
>> ```python3
>> >>> msns = h.missions.get_available()
>> >>> h.missions.set_status(msns[0], 'CLAIM')
>> {'target': 'jwfplgu', 'title': 'Some Mission', 'payout': 50,
>>     'status': 'CLAIMED', 'success': True}
>> >>> h.missions.set_status(msns[0], 'DISCLAIM')
>> {'target': 'jwfplgu', 'title': 'Some Mission', 'payout': 50,
>>     'status': 'DISCLAIMED', 'success': True}

