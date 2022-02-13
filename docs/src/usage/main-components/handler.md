# Handler

The Handler is responsible for, you guessed it, handling the flow of data and functions within the SynackAPI package.

Being totally honest, this isn't strictly required, but it definitely makes things easier.

It is instantiated after `import synack` as seen in the following example:

```python3
#!/usr/bin/env python3

import synack

h = synack.Handler()
```

From there, you can use any of the Plugins as follows:

```
h.missions.get_count()
h.targets.set_registered()
```

## Setting One-Off States

It's important to note that you can easily change some of the State variables by passing them into the Handler.

For example, if you want to see all requests being made in the current script, you can enable debugging as following:

```python3
h = synack.Handler(debug=True)
h.targets.do_register_all()
```
