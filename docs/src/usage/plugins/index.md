# Plugins

Within the SynackAPI, various "Plugins" exist to allow us to easily separate functions based on their purpose.

## Function Naming Convension

Similar to PowerShell, functions within this package will begin with a verb.
This is a list of approved verbs and their meaning.

| Verb | Description
| --- | ---
| add | Insert/Update item(s) in the Database
| build | Change data/items in some way
| find | Query the Database
| get | Retrieve Data from the Synack API or Local Files
| remove | Delete item(s) from the Database
| set | Push changes to the Synack API or Local Files

Additionally, function names should not be redundant.
In other words, consider the function name `missions.get_missions()`.
`missions` is specified twice, when `missions.get()` is just as clear.
`missions.get()` is the optimal choice.
