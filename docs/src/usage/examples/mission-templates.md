# Mission Templates

I am going to start off this page with a technical explanation of how you can implement templates, then explain some template basics to help you think through how you may wish to build your template library.

## Usage

This section will show you how to implement a very simple bot to take in templates stored on your disk and upload them to your claimed missions.


```python3
#!/usr/bin/env python3

import synack

def replace_placeholders(template, mission):
    """Replace placeholders in a misson template

    Down below, I mention how you could drop credentials
    into a template on the fly. This is a super simple
    example of how that sort of thing could be done.
    It would replace any instance of __CODENAME__ with
    the actual codename of the target
    """
    for k in template.keys():
        template[k] = template[k].replace('__CODENAME__',
                                          mission['listingCodename'])

h = synack.Handler()

msns = h.missions.get_claimed()

for m in msns:
    template = h.missions.get_file(m)
    if template:
        template = replace_placeholders(template)
        h.missions.set_evidences(m, template)

```

### File Structure

It is important to understand the file structure of your mission templates.

The default location for templates is `~/Templates`, but this could be overridden by setting `template_dir` in the [State](../main-components/state.md).

Each mission from the Synack API has a couple of attributes I use to build the file structure.
There is the `taskType` (`MISSION`, `SV2M`, etc), the `asset`/`assetTypes` (`host', 'web', 'ios', 'android', etc.), and the `title` (Name of the mission).
Each of these attributes are run thorough `templates.build_safe_name()`, which makes everything lowercase and removes special characters to make sure there are no issuer with the name of the file.

As an example, the following mission will turn into the following filepath:

```
>>> mission = {
...     "taskType": "MISSION",
...     "assetTypes": ["web"],
...     "title": "SOMe Cr@Z33 Misson Name: The Sequel"
... }
>>> targets.build_filepath(mission)
'/home/jojo/Templates/mission/web/some_cr_z33_mission_name_the_sequel.txt'
```

## Template Basics

As someone who is part of the Synack Auto Approve group, I attribute a lot of my success with missions to my templates.
Hopefully this section will help you understand some of my main considerations when doing templates/missions.

This section ended up being quite a bit longer that I originally anticipated, but hopefully you find it useful.

### Spend the time to make a good template/report

When you are making a template for the first time, make it very good.
The more time you put in the first time, the less time you need to put into the report each additional time while still having a very solid report.

It is not uncommon for me to spend an hour or more the first time I do a mission regardless of whether it is a $15 or a $100 mission.
It seems like a lot of time, but if it is done properly, it really helps you speed through any time you are able to get that mission in the future.

Also consider that your goal is to make the report good enough that VulnOps will not reject it AND that the customer is HAPPY with the outcome.
It may be tempting to think about missions as a "quick $X", this is the absolute wrong way to think about them.
Instead, you should consider it as you selling the idea that the client should purchase more missions from Synack and encourage their peers to do the same.
While a crappy mission may BARELY squeeze by VulnOps, if it doesn't make the client happy, this means less missions for you in the future.

With that in mind, I strongly encourage you to set the goal on making sure the client will be happy, which will result in more missions for you in the future.

### Spend a lot of time on the Introduction and Tools section

I personally find the Introduction and first part of the Testing Methodology sections to be the most important sections of the entire report when doing a mission for the first time.
This may sound insane because the Details of how the mission was done and Summary seem like they would be the most important, so let me explain.

The Introduction section and beginning of the Testing Methodology section can be used to CLEARLY and CONSICELY explain why you are working right this second, what your goals are, and how you are going to make a determination on whether the client asset is vulnerable or not.

This is not only for the client, but I also find it incredibly useful for myself.
When knocking out a large number of missions, it is easy to forget the details of what exactly you are doing on a specific mission.
Having that information readily available lets me jump into the mission much quicker than if I had to think about it.

As an example of what this may look like, consider the following mission template snippets:

> Introduction
>
> 
>> This mission requests that we determine whether or not the target accepts default credentials as defined in the [OWASP WSTG](https://github.com/synack/wstg/blob/master/document/4-Web_Application_Security_Testing/04-Authentication_Testing/02-Testing_for_Default_Credentials.md).
>>
>> Some applications come with default credentials configured out of the box. These default credentials can be very easy to guess if the software is well known and/or they are trivial. To make matters worse, these default credentials often provide access to highly-privileged users, such as Administrators. As such, it is highly recommended that they be changed as soon as possible to prohibit attackers from easily being able to control your application.
> 
> Testing Methodology
>
>> \# Plan
>>
>> 1. Determine software used within this target
>> 2. Attempt Default Credentials, if found
>> 3. Attempt common credentials
>>
>> \# Tools / Resources
>> 
>> * Burp Suite Pro: Network proxy that allow for the interception, modification, and automated testing of network requests and endpoints
>> * [Common Usernames](https://raw.githubusercontent.com/danielmiessler/SecLists/master/Usernames/top-usernames-shortlist.txt): A list of very common usernames 
>> * [Common Passwords](https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/top-passwords-shortlist.txt): A list of very common passwords
>> 
>> \#\# Accounts
>>
>> No provided credentials were used in this mission.
>> 
>> \# Details.
>>
>> ... 

With this information already compiled for you, you have something that looks professional and is ready to be submitted.
It also instantly reminds you that you will be using Burp to try and determine the software used so you can try specific credentials, then falling back to a pre-decided list of usernames and passwords you can throw into Burp Intruder so you don't have to spend time looking for a good list.

### Provide a spot for credentials

While in this specific template, Account credentials are not provided, if this were not the case, that section would look similar to the following.

> Testing Methodology
>
>> \#\# Accounts
>>
>> Username: `Bob`
>> Password: `password1234`
>> Auth URL: \[https://login.company.com\](https://login.company.com)

Because this is not going to be the same between missions, the details should not be filled in.
One way to do this would be to have the structure of this section in the template so it can be very easily filled in.
If you were feeling exceptionally fancy, it also wouldn't be insane to use the `targets.get_credentials()` function to pull credentials, format them, then use something like the python `re` package to inject the credentials into your templates before they are uploaded.

### Be clear and detailed, but generic

Any time that I get a mission I do not have a template for, I will sit down and write the best report that I possibly can, while trying to keep it relatively generic.

As an example, I will write them similar to the following:

> Yes
> 
>> \#\# Phase 1
>>
>> I began my research by visiting the client website seen in **1.1.png**. I then installed magic as can be seen in **1.2.png**. As can be seen in **1.3.png**, the installation was successful and I was given access to the mainframe.
>
> No
>> 
>> \#\# Phase 1
>>
>> I began my research on SLEEPYPUPPY by visiting `http://www.supersleepy.dog/secret/cat-pics` as seen in **cat-pics.png**. I then installed magic as can be seen in **magiccat.png**. As can be ssen in **puppymainframe.png**, the installation was successful and I was given access to the SLEEPYPUPPY mainframe.

Both of these segments would be a good start to a mission and provide the client with the information they need in a clear and concise way, but when I need to do this same mission on CATNIPPEDKITTY, the second example means that I need to change a ton of information within the report before I can submit it. Having to 


### Consider where you will need to deviate from generic templates

Sometimes, it isn't possible to make a report both good AND generic.
When these situations arise, consider how you will handle it while fixing up your templates.

As an example, consider a situation where you are testing SQL Injection and need to explain your work in text.
Making a template like this would allow you to easily identify that you need to explain your work.

> \#/# Phase 2
>
> ... I was able to achieve a SQL Injection as seen in **2.3.png** by changing \_\_VARIABLE\_\_ to \_\_SQLI\_\_.
>
> \_\_EXPLAIN_MORE_ABOUT_THE_SQLI\_\_

When reviewing your mission, these will stick out, and you can identify that you need to change them.
