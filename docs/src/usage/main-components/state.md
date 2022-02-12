# State

The State object tracks several variables for a single instance of the Handler.

As seen in the following example, you can create a State variable externally and control it there.
In the event that you do not pass in a State, one is created automatically.
You can also continue to manipulate the State in the ways shown below.



```
#!/usr/bin/env python3

import synack

state = synack.State()
state.debug = True
handler = synack.Handler(state)
handler.debug.log("Test", "This message WILL be seen")
handler.state.debug = False
handler.debug.log("Test", "This message will NOT be seen")
state = True
handler.debug.log("Test", "This message WILL be seen")

# ----- OR -----

handler = synack.Handler(debug=True)
handler.debug.log("Test", "This message WILL be seen")
handler.state.debug = False
handler.debug.log("Test", "This message will NOT be seen")
handler.state.debug = True
handler.debug.log("Test", "This message WILL be seen")
```


## Database vs State

The observant will notice that there is a lot of overlap between the values stored in the Database and the State.
This may cause you some confusion as to where data is coming from and how it's being stored and accessed.

The Database contains **persistant** or **shared** information.
For example, the api_token, which should be shared by all Handlers or cached Target information that could be quickly referenced.

The State only persists within **one** instance of the Handler.
In the event that one of the State variables is set and is **not** constantly at risk of being changed (such as the api_token), the value stored in the State will be provided **instead of** the Database value. This is useful when you want to **override** Database variables in a single Handler. For example, you may wish to enable the `debug` variable for a single Handler without affecting other Handlers you may have running.

## Variables

| Variable | Type | Description
| --- | --- | ---
| api_token | str | This is the Synack Access Token used to authenticate requests
| config_dir | pathlib.Path | The location of the Database and Login script
| debug | bool | Used to show/hide debugging messages
| email | str | Your email address used to log into Synack
| http_proxy | str | A Web Proxy (Burp, etc.) to intercept requests
| https_proxy | str | A Web Proxy (Burp, etc.) to intercept requests
| login | bool | Used to enable/disable a check of the api_token upon creation of the Handler
| notifications_token | str | Token used for authentication when dealing with Synack Notifications
| otp_secret | str | OTP Secret held by Authy. NOT an OTP. For more information, read the Usage page
| password | str | Your Synack Password
| session | requests.Session | Tracks cookies and headers across various functions
| template_dir | pathlib.Path | The location of your Mission Templates
| use_proxies | bool | Enables/Disables Web Proxy Usage
| user_id | bool | Your Synack user id used in many requests
