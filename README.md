# Library for interacting with Synack API 

This is a library and set of scripts that make SRT life a little easier when interacting with the platform from a linux commandline.
* Connect to platform
  * Stay connected to the platform
* Register available targets
* Connect to targets
* Download targets' scope
* Retrieve analytics from `Web Application` and `Host` targets
* Download hydra findings
* Retrieve target specific information:
  * Client names
  * Codenames
  * Slugs
  * Target types
* Enable mission-claiming bots
* Manage notifications

# Acknowledgements

This is a rework of the SynackAPI originally created by gexpose, with the help of Malcolm, Nicolas, and pmnh.

Please visit the orginal project at:
https://github.com/gexpose/synackAPI

# Configuration / Installation
## Operating System

This has been developed on/for Linux. It will not work on Windows because certain things are expected to be certain places (such as the config file). Maybe I'll get around to adding Windows support in the future, but I wouldn't count on it. If you're interested in helping out with that, feel free.

## Installation

The easiest way to install this is as follows:

```
python3 -m pip install synack
```

## Configuration Directories
The required directory is `~/.config/synack`. If this folder doesn't already exist, it will be created when you first create a Handler object.

## ~/.config/synack/config
This is a required config file. If it is not created already, you will be prompted to fill in the variables when you first create a Handler object.
```
api_token: ...
debug: false
email: synack@srt.io
otp_secret: ...
password: ...
proxies:
  http: http://127.0.0.1:8080
  https: http://127.0.0.1:8080
use_proxies: false
```

* api_token: The last successful API token so it can be reused
* debug: Enables debug mode by default to increase verbosity
* email: The email address you use to log into the platform
* password: The password you use to log into the platform
* otp_secret: base32 secret for generating Authy tokens
  * Guillaume Boudreau provide a nice [walk through](https://gist.github.com/gboudreau/94bb0c11a6209c82418d01a59d958c93) for getting this secret
    * Follow the above to get Authy into debug mode, then use [THIS CODE](https://gist.github.com/louiszuckerman/2dd4fddf8097ce89594bb33426ab5e23#ok-thats-nice-but-i-want-to-get-rid-of-authy-now) to get your valid TOTP SECRET!
* proxies: The http/https proxies to use if use_proxies is true

# Usage

This python3 module provides a class to create objects for interacting with the Synack LP/LP+ platform.

## Examples

Examples can be found in the `examples` directory.

You can use this to create full scripts, but part of my desire to refactor came from simplification of oneliners.
For example, you could create the following cron job to register all unregistered targets every 30 minutes:

```
*/30 * * * * python3 -c 'import synack; h = synack.Handler(); h.targets.do_register_all();'

```

### synack.Handler()

A Handler object is created to keep track of data across the entire script.
Upon creation, the api_token in your config file is automatically tested and renewed if necessary

### synack.Handler().targets.do_register_all()

Takes the Handler and performs a series of requests to get a list of all unregistered targets and register them.
