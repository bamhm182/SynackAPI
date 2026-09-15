# Transactions

## transactions.get(period='', max_pages=1, page=1, per_page=15)

> Returns transaction history. If a page is full and `page < max_pages`, subsequent pages are fetched recursively.
>
> | Arguments | Type | Description
> | --- | --- | ---
> | `period` | str | Period filter sent to Synack. Empty string uses the default API behavior.
> | `max_pages` | int | Maximum number of pages to request
> | `page` | int | First page to request
> | `per_page` | int | Transactions per page
>
>> Examples
>> ```python3
>> >>> h.transactions.get(max_pages=2)
>> [{"amount": "10.0", ...}, ...]
>> ```

## transactions.get_balance()

> Returns information about your current account balance and pending payouts.
>
>> Examples
>> ```python3
>> >>> h.transactions.get_balance()
>> {"total_balance": "30.0", "pending_payout": "0.0"}
>> ```
