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
>> >>> h.db.synack_url = 'https://hooks.slack.com/services/x/y/z'
>> >>> h.alerts.slack('Something important happened!')
>> ```
