# Files

## synackapi.db

This is a SQLite Database which exists at `~/.config/synack/synackapi.db` and stores your permanent settings and caches some data from the Synack API.

Information such as your email, password, and OTP Secret exist here.
**Keep it protected!**

Some information is automatically cached so that the number of redundant requests you need.
For example, if you pull a lot of Target information, there is a good chance that some of the basic information (slug, codename, etc.) will not change.
Once it's pulled the first time, the SQLite Database will hold some of the information so that you can do things like converting Slugs to Codenames and vice versa without sending a request to Synack's API.

Another example would be the Synack Access Token, which is what authenticates you and is used to make requests.
There is no reason to generate a new Access Token every time your Handler is initiated, so when you log in, it is stored in the database.
When you make a new Handler, it will try to use this token.
If it's valid, it will jump into the requested function, otherwise, it will complete the login workflow, then move onto the requested function.

## login.js

This is a JavaScript file which exists at ~/.config/synack/login.js and aids in keeping you logged in.
It is intended to be used with the following TamperMonkey script in order to do the following:

1. See you are on `https://login.synack.com`
1. Wait 60 seconds
1. Redirect you to `https://platform.synack.com`
1. Inject your current Access Token into Chrome


```javascript
// ==UserScript==
// @name         Synack
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  Go to the platform automatically
// @author       You
// @run-at       document-start
// @match        https://*.synack.com/*
// @require      file:///home/<homedir>/.config/synack/login.js
// @grant        none
// ==/UserScript==


alert('Change the require line to point to the right place and delete this line. Also modify tampermonkey to be able to read local files. This is probably really dumb, so I will not tell you how to do this in an effort to make certain you have thought it through.');
```

Note: You must change the @require line to the location of the `login.js` file.
Additionally, you will want to delete the `alert()`.
