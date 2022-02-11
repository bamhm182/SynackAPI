# Mission Bot

This is a simple example of how you could determine if there are missions every 30 seconds, try to claim some if there are.

We start by using `import synack` to bring in the SynackAPI package.
We then use `h = synack.Handler()` to create the primary object we will be using; the Handler.
All plugins are a part of the handler, which allows us to use `h.missions.get_missions_count()` to make a lightweight HEAD request to determine the number of missions. If there are **currently** more missions than we **know** about from our last check, we can assume that some missions were released. We can then use `h.missions.get_available_missions()` to get a list of available missions, and request them one at a time with `h.missions.do_claim_mission(m)`. When the number of current missions goes back down to 0, we can assume there are no missions left, and we can reset our known missions to `0`.



```python
#!/usr/bin/env python3

import time
import synack

h = synack.Handler()

known_missions = 0

while True:
    time.sleep(30)
    curr_missions = h.missions.get_missions_count()
    if curr_missions > known_missions:
        known_missions = curr_missions
        msns = h.missions.get_available_missions()
        for m in missions:
            time.sleep(1)
            h.missions.do_claim_mission(m)
    elif curr_missions == 0:
        known_missions = 0
```
