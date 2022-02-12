# Check Invisible Missions

This was originally part of the main package, but it's pretty noisy, so I removed it so people wouldn't accidentally run it.

Sometimes a condition will arise in which the sidebar states there are missions, but there are not.
These missions are associated with a specific target.
If this happens, we can use this script to easily determine which target has the mission so you can submit a ticket.

This is going to pull a list of all targets you're registered to and cache it in the Database with `h.targets.get_registered_summary()`.
It then iterates through them and asks for a mission count with a HEAD request for every single target individually (`h.missions.get_count()`.
If a target reports it has missions, it then tries to pull a full list of its missions with `h.missions.get()`.
If there are no missions, it adds the codename to a list, which is printed out at the end.

**This will make several hundred requests (1 HEAD, 1 GET for EVERY Target).**
**DO NOT use it unless you understand the implications and are trying to track down an invisible mission so Synack can fix it.**

```python3
#!/usr/bin/env python3

import synack
import time

h = synack.Handler()

h.targets.get_registered_summary()

for t in h.db.targets:
    time.sleep(1)
    count = h.missions.get_count("PUBLISHED", t.slug)
    if count > 0:
        missions = h.missions.get("PUBLISHED", 1, 1, count, t.slug)
        if len(missions) == 0:
            print(t.codename)
```
