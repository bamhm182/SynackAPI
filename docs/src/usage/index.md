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
This prompt will expect the `Synack Email` and `Synack Password`, which are fairly self explanatory.

For Duo MFA setup options, see the [Duo plugin documentation](./plugins/duo.md).

Once you complete these steps, your credentials are stored in a SQLiteDB at `~/.config/synack/synackapi.db`.
