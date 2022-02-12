# Patches

This is a terrbile way to handle this, but it technically works.
v0.1 saw a HUGE refactor and I broke some things.
While I am working out the kinks, you can run these commands to 'patch' your version.

Once I get everything fixed, I will release v0.1.2.

## v0.1.1

```
sed -i 's/filter_targets/find_targets/g' ~/.local/lib/python3.10/site-packages/synack/plugins/targets.py
```
