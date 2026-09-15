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

## scratchspace.set_assets_file(content, target=None, codename=None)

> This function will save a `assets.txt` scope file within a `codename` folder within the `self.db.scratchspace_dir` folder
> If `self.db.use_scratchspace` is `True`, this function is automatically run when you do `targets.get_scope()` or `targets.get_scope_web()`
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `content` | str,list(str) | Either a preformatted string or (more likely) the return of `targets.get_scope()`
> | `target` | db.models.Target | A Target Database Object
> | `codename` | str | Codename of a Target
>
>> Examples
>> ```python3
>> >>> scope = h.targets.get_scope_web(codename='ADAMANTANT')
>> >>> h.scratchspace.set_assets_file(scope, codename='ADAMANTANT')
>> '/tmp/Scratchspace/ADAMANTANT/assets.txt'
>> ```

## scratchspace.set_burp_file(content, target=None, codename=None)

> This function will save a `burp.txt` scope file within a `codename` folder within the `self.db.scratchspace_dir` folder
> If `self.db.use_scratchspace` is `True`, this function is automatically run when you do `targets.get_scope()` or `targets.get_scope_web()`
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `content` | str,list(str) | Either a preformatted string or (more likely) the return of `targets.get_scope()`
> | `target` | db.models.Target | A Target Database Object
> | `codename` | str | Codename of a Target
>
>> Examples
>> ```python3
>> >>> scope = h.targets.get_scope_web(codename='ADAMANTANT')
>> >>> h.scratchspace.set_burp_file(scope, codename='ADAMANTANT')
>> '/tmp/Scratchspace/ADAMANTANT/burp.txt'
>> ```

## scratchspace.set_download_attachments(attachments, target=None, codename=None, prompt_overwrite=True):

> This function will take a list of attachments from `h.targets.get_attachments()` and download them to the `codename` folder wthin the `self.db.scratchspace_dir` folder.
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `attachments` | list(dict) | A list of attachments from `h.targets.get_attachments()`
> | `target` | db.models.Target | A Target Database Object
> | `codename` | str | Codename of a Target
> | `prompt_overwrite` | bool | Boolean to determine if you should be prompted before overwriting an existing file
>
>> Examples
>> ```python3
>> >>> attachments = h.targets.get_attachments()
>> >>> slug = attachments[0].get('listing_id')
>> >>> codename = h.targets.build_codename_from_slug(slug)
>> >>> h.scratchspace.set_download_attachments(attachments, codename=codename)
>> [PosixPath('/home/user/Scratchspace/SLEEPYTURTLE/file1.txt'), ...]
>> ```
>> ```python3
>> >>> h.scratchspace.set_download_attachments(attachments, codename=codename)
>> file1.txt exists. Overwrite? [y/N]: Y
>> [PosixPath('/home/user/Scratchspace/SLEEPYTURTLE/file1.txt'), ...]
>> >>> h.scratchspace.set_download_attachments(attachments, codename=codename)
>> file1.txt exists. Overwrite? [y/N]: N
>> []
>> >>> h.scratchspace.set_download_attachments(attachments, codename=codename, prompt_overwrite=False)
>> [PosixPath('/home/user/Scratchspace/SLEEPYTURTLE/file1.txt'), ...]
>> ```

## scratchspace.set_file(content, filename, target=None, codename=None)

> This function will save a text file with a given name within a `codename` folder within the `sself.db.scratchspace_dir` folder.
> If `self.db.use_scratchspace` is `True`, this function is automatically run when you do `targets.get_scope()` or similar.
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `content` | str,list(str) | Either a preformatted string or (more likely) the return of `targets.get_scope_host()`
> | `filename` | str | Desired filename
> | `target` | db.models.Target | A Target Database Object
> | `codename` | str | Codename of a Target
>
>> Examples
>> ```python3
>> >>> h.scratchspace.set_file('some unique string', 'mystring.txt', codename='ADAMANTARDVARK')
>> '/tmp/Scratchspace/ADAMANTARDVARK/mystring.txt'
>> ```

## scratchspace.set_hosts_file(content, target=None, codename=None)

> This function will save a `hosts.txt` scope file within a `codename` folder within the `self.db.scratchspace_dir` folder.
> If `self.db.use_scratchspace` is `True`, this function is automatically run when you do `targets.get_scope()` or `targets.get_scope_host()`
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `content` | str,list(str) | Either a preformatted string or (more likely) the return of `targets.get_scope_host()`
> | `target` | db.models.Target | A Target Database Object
> | `codename` | str | Codename of a Target
>
>> Examples
>> ```python3
>> >>> scope = h.targets.get_scope_host(codename='ADAMANTARDVARK')
>> >>> h.scratchspace.set_hosts_file(scope, codename='ADAMANTARDVARK')
>> '/tmp/Scratchspace/ADAMANTARDVARK/hosts.txt'
>> ```

