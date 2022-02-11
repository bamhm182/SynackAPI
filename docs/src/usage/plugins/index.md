# Plugins

Within the SynackAPI, various "Plugins" exist to allow us to easily separate functions based on their purpose.

## Function Naming Convension

I am trying to keep to the following naming conventions:
* No redundancy (`h.missions.get_approved()` good, `h.missions.get_approved_missions()` bad)
* `h.plugin.get_*` functions intend to get data from the Synack API
* `h.plugin.do_*` functions intend to do something with retrieved data or make changes via the Synack API
