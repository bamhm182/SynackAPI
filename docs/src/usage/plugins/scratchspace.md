# Scratchspace

## scratchspace.build_filepath(filename, target=None, codename=None)

> This function return the desired Scratchspace file name based on `db.scratchspace_dir` and a Target's Codename.
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `filename` | str | Desired name of the destination file
> | `target` | db.models.Target | A Target Database Object
> | `codename` | str | Codename of a Target
>
>> Examples
>> ```python3
>> >>> h.scratchspace.buildfilepath('test', codename='ADAMANTANT')
>> '/tmp/Scratchspace/ADAMANTANT/test.txt'
>> ```

## scratchspace.set_burp_file(content, target=None, codename=None)

> This function will save a `burp.txt` scope file within a `codename` folder in within the `self.db.scratchspace_dir` folder
> If `self.db.use_scratchspace` is `True`, this function is automatically run when you do `self.targets.get_scope()` or `self.targets.get_scope_web()`
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `content` | str,list(str) | Either a preformatted string or (more likely) the return of `self.targets.get_scope_host()`
> | `target` | db.models.Target | A Target Database Object
> | `codename` | str | Codename of a Target
>
>> Examples
>> ```python3
>> >>> scope = h.targets.get_scope_web(codename='ADAMANTANT')
>> >>> h.scratchspace.set_hosts_file(scope, codename='ADAMANTANT')
>> '/tmp/Scratchspace/ADAMANTANT/burp.txt'
>> ```

## scratchspace.set_hosts_file(content, target=None, codename=None)

> This function will save a `hosts.txt` scope file within a `codename` folder in within the `self.db.scratchspace_dir` folder
> If `self.db.use_scratchspace` is `True`, this function is automatically run when you do `self.targets.get_scope()` or `self.targets.get_scope_host()`
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `content` | str,list(str) | Either a preformatted string or (more likely) the return of `self.targets.get_scope_host()`
> | `target` | db.models.Target | A Target Database Object
> | `codename` | str | Codename of a Target
>
>> Examples
>> ```python3
>> >>> scope = h.targets.get_scope_host(codename='ADAMANTARDVARK')
>> >>> h.scratchspace.set_hosts_file(scope, codename='ADAMANTARDVARK')
>> '/tmp/Scratchspace/ADAMANTARDVARK/hosts.txt'
>> ```
