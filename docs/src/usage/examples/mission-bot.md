# Mission Bot

This is a simple example of how you could determine if there are missions every 30 seconds, try to claim some if there are.

We start by using `import synack` to bring in the SynackAPI package.
We then use `h = synack.Handler()` to create the primary object we will be using; the Handler.
All plugins are a part of the handler, which allows us to use `h.missions.get_count()` to make a lightweight HEAD request to determine the number of missions. If there are **currently** more missions than we **know** about from our last check, we can assume that some missions were released. We can then use `h.missions.get_available()` to get a list of available missions, and request them one at a time with `h.missions.set_claimed(m)`. When the number of current missions goes back down to 0, we can assume there are no missions left, and we can reset our known missions to `0`.



```python
#!/usr/bin/env python3

import time
import synack

h = synack.Handler(login=True)
print("I just logged in and if it was the first time I logged in, I successfully filled out my credentials!")

known_missions = 0
print("Since I just started looking, I don't know about any missions!")

while True:
    print("I had better sleep for a while so that I don't blow up the API, get everyone mad at me, and get myself banned!")
    time.sleep(30)
    curr_missions = h.missions.get_count()
    print(f"There are {curr_missions} missions")
    if curr_missions and curr_missions > known_missions:
        print("There are new missions I didn't know about!")
        known_missions = curr_missions
        missions = h.missions.get_available()
        print(f"I grabbed a list of {len(missions)} missions!")
        for m in missions:
            print("I had better sleep for a while so that I don't blow up the API, get everyone mad at me, and get myself banned!")
            time.sleep(1)
            outcome = h.missions.set_claimed(m)
            print(f"I tried to claim a mission. You can see the outcome here: {outcome}")
    elif curr_missions == 0:
        print("There are currently no missions, I'd better remember that!")
        known_missions = 0
```
