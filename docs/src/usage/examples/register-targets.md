# Register Targets

One of the main goals for this project was to be able to create super simple oneliners that I could throw into various places like my i3blocks status bar.

To show you how this can be done, let's take a look at the following example, which will register all unregistered targets for you.

If you're unfamiliar with `python3 -c`, this is how you can execute a small amount of Python from your (bash, zsh, etc.) shell.
We take that to `import synack` just as we would in a full script.
We then have a longer command that creates the handler, then calls the `targets.do_register_all()` function to get and register all unregistered targets.

```bash
python3 -c "import synack; synack.Handler().targets.do_register_all()"
```

This could be thrown into a cronjob (`crontab -e`) as seen below to register any new targets once an hour:

```sh
0 * * * * python3 -c "import synack; synack.Handler().targets.do_register_all()"
```
