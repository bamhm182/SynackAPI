# Notifications

## notifications.get()

> Return a list of notifications
>
>> Examples
>> ```python3
>> >>> h.notifications.get()
>> [{"action": "outage_starts", "subject": "SLAPHAPPYMONKEY",...}...]
>> ```

## notifications.get_unread_count()

> Get the number of unread notifications
>
>> Examples
>> ```python3
>> >>> h.notifications.get_unread_count()
>> 7
>> ```

## notifications.set_read()

> Set all notifications as read
>
>> Examples
>> ```python3
>> >>> h.notifications.set_read()
>> ```
