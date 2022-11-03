# Usage

The easiest way to get started with the SynackAPI is to install it via `pip`.
For example:

```bash
pip3 install --upgrade SynackAPI
```

After doing this, you can use one of the [Examples](./examples/index.md) to understand the basic usage of the package.

I am not going to provide you with a ton of awesome scripts that will leverage the SynackAPI package.
That is on you.

With that in mind, I would highly recommend you become familiar with the [Plugins](./plugins/index.md) provided and apply your own ingenuity to come up with your own scripts.

## Authentication

The first time you try to do anything which requires authentication, you will be automatically prompted for your credentials.
This prompt will expect the `Synack Email` and `Synack Password`, which are fairly self explanitory, but it also asks for the `Synack OTP Secret`.

The `Synack OTP Secret` is NOT the 8 digit code you pull out of Authy.
Instead, it is a string that you must extract from Authy via a method similar to the one found [here](https://gist.github.com/gboudreau/94bb0c11a6209c82418d01a59d958c93).

Use the above instructions at your own discression.
I TAKE NO RESPONSIBILITY IF SOMETHING BAD HAPPENS AS A RESULT.

Once you complete these steps, your credentials are stored in a SQLiteDB at `~/.config/synack/synackapi.db`.
