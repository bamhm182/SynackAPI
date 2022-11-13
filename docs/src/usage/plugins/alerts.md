# Alerts

The Alerts Plugin is used to send alerts to various external services.

The functions within this plugin don't follow the standard naming convention.

## alerts.email(subject, message)

>> This function attempts to use SMTP to send an email.
>> This function expects `h.db.smtp_x` attributes to have been set.
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `subject` | str | Email Subject
> | `message` | str | Email Message
>
>> Examples
>> ```python3
>> >>> h.db.smtp_server = 'smtp.email.com'
>> >>> h.db.smtp_port = 465
>> >>> h.db.smtp_starttls = True
>> >>> h.db.smtp_username = 'me@email.com'
>> >>> h.db.smtp_password = 'password123'
>> >>> h.db.smtp_email_to = 'you@email.com'
>> >>> h.db.smtp_email_from = 'me@email.com'
>> >>> h.alerts.email('Look out!', 'Some other important thing happened!')
>> ```

## alerts.sanitize(message):

> This function aims to remove URLs, IPv4, and IPv6 content from a given message.
> Sometimes Synack puts sensitive URLs and IP addresses in content like Mission Titles,
> so if you are sending these through 3rd party networks (Slack, Discord, Email, SMS, etc.),
> please make sure that you do you due dilligence to ensure you aren't sending client information.
>
> This function has been tested to ensure a wide variety of sensitive data is stripped, but it might
> not be all inclusive. If you find sensitive data that it doesn't properly sanitize, please let me
> know and we'll get it addressed.
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `message` | str | A message to sanitize
>
>> Examples
>> ```python3
>> >>> h.alerts.sanitize('This is an IPv4: 1.2.3.4')
>> This is an IP: [IPv4]
>> >>> h.alerts.sanitize('This is an IP: 1234:1d8::4567:2345')
>> This is an IPv6: [IPv6]
>> >>> h.alerts.sanitize('This is a URL: https://something.com')
>> This is a URL: [URL]
>> ```

## alerts.slack(message)

> This function makes a POST request to Slack in order to post a message.
> This function expects `h.db.slack_url` to be set.
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `message` | str | A message to send to Slack
>
>> Examples
>> ```python3
>> >>> h.db.slack_url = 'https://hooks.slack.com/services/x/y/z'
>> >>> h.alerts.slack('Something important happened!')
>> ```
