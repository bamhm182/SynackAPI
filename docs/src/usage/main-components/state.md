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

Out of all of the State variables, `login` is the most important to understand.
If this is set to true, whenever your Handler is created, it will make sure you are logged in.
If you have a bunch of scripts based on SynackAPI, it is probably a good idea to have `login` set to False, which is the default, for the majority of scripts.
Then you can have a couple scripts which are run periodically with `login` set to True so it becomes responsible for making sure that everything is logged in.

As an example of a good function to set `login` to True, check out the [Register Targets](../examples/register-targets.md) Example.

## Database vs State

The observant will notice that there is a lot of overlap between the values stored in the Database and the State.
This may cause you some confusion as to where data is coming from and how it's being stored and accessed.

The Database contains **persistent** or **shared** information.
For example, the api_token, which should be shared by all Handlers or cached Target information that could be quickly referenced.

The State only persists within **one** instance of the Handler.
In the event that one of the State variables is set and is **not** constantly at risk of being changed (such as the api_token), the value stored in the State will be provided **instead of** the Database value. This is useful when you want to **override** Database variables in a single Handler. For example, you may wish to enable the `debug` variable for a single Handler without affecting other Handlers you may have running.

## Variables

| Variable | Type | Description
| --- | --- | ---
| api_token | str | This is the Synack Access Token used to authenticate requests
| config_dir | pathlib.Path | The location of the Database and Login script
| debug | bool | Used to show/hide debugging messages
| duo_akey | str | Duo virtual-device application key used for push approval
| duo_host | str | Duo API hostname used for push approval
| duo_pkey | str | Duo virtual-device push key used for request signing
| duo_rsa_key | str | RSA private key used to sign Duo virtual-device push requests
| email | str | Your email address used to log into Synack
| http_proxy | str | A Web Proxy (Burp, etc.) to intercept requests
| https_proxy | str | A Web Proxy (Burp, etc.) to intercept requests
| login | bool | Used to enable/disable a check of the api_token upon creation of the Handler
| notifications_token | str | Token used for authentication when dealing with Synack Notifications
| otp_count | int | HOTP counter used for Duo offline passcodes
| otp_secret | str | OTP Secret held by Duo Mobile. NOT an OTP. For more information, read the Usage page
| password | str | Your Synack Password
| proxies | dict | Requests proxy mapping built from `http_proxy` and `https_proxy` when `use_proxies` is enabled
| scratchspace_dir | pathlib.Path | The location of scratchspace files
| session | requests.Session | Tracks cookies and headers across various functions
| slack_app_token | str | Slack app-level token used for Notifications
| slack_channel | str | Slack channel used for Notifications
| slack_url | str | Slack webhook URL used for Notifications
| smtp_email_from | str | Source address for SMTP notifications
| smtp_email_to | str | Destination address for SMTP notifications
| smtp_password | str | Password for SMTP notifications
| smtp_port | int | Port for SMTP notifications
| smtp_server | str | Server for SMTP notifications
| smtp_starttls | bool | Whether SMTP notifications should use STARTTLS
| smtp_username | str | Username for SMTP notifications
| synack_domain | str | Synack domain to use for login/platform URLs
| template_dir | pathlib.Path | The location of your Mission Templates
| use_proxies | bool | Enables/Disables Web Proxy Usage
| use_scratchspace | bool | Enables/disables writing scope and attachment files to scratchspace
| user_id | str | Your Synack user id used in many requests
