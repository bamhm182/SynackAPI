# Duo

## Duo MFA Options

When prompted during authentication, you can choose from three options:

**Option 1: Manual Push Approval (Simplest)**
- Press Enter when prompted for OTP Secret
- Approve push notifications on your phone each time the token is expired
- No additional setup required

**Option 2: Automated OTP (Preferred)**
- Enter your OTP Secret when prompted (accepts both hex and base32 formats)
- Automatically generates OTP codes using a counter (saved in the database)
- Extract the `hotp_secret` from Duo Mobile using [synackDUO](https://github.com/dinosn/synackDUO) (see `response.json`)
- **Note:** This is NOT the 8-digit codes from Duo Mobile, but the HOTP secret key

**Option 3: Automated Duo Push**
- Uses Duo credentials to auto-approve push requests
- Can also approve push requests using duo.approve_pending_push(timeout)
- Extract credentials using [synackDUO](https://github.com/dinosn/synackDUO) (see `response.json`) (see below)


**Disclaimer:** Use the above instructions at your own discretion. I TAKE NO RESPONSIBILITY IF SOMETHING BAD HAPPENS AS A RESULT.

## Duo Push Auto-Approval Setup

The Duo plugin supports push notification approval using device credentials.

### Prerequisites

You must extract and configure four credentials from Duo Mobile:

| Credential | Description | Example
| --- | --- | ---
| `duo_push_akey` | Device activation key | `DAXXXXXXXXXXXXXXXXXXXX`
| `duo_push_pkey` | Device private key | `DPXXXXXXXXXXXXXXXXXXXX`
| `duo_push_host` | Duo API hostname | `api-xxxxxxxx.duosecurity.com`
| `duo_push_rsa_key_path` | Path to RSA private key | `~/.config/synack/duo/key.pem`

### Configuration

Set credentials in the database:
PP
```python
import synack

h = synack.Handler(login=False)

h.db.set_config('duo_push_akey', 'DAXXXXXXXXXXXXXXXXXX')
h.db.set_config('duo_push_pkey', 'DPXXXXXXXXXXXXXXXXXX')
h.db.set_config('duo_push_host', 'api-xxxxxxxx.duosecurity.com')
h.db.set_config('duo_push_rsa_key_path', 'synackDUO/key.pem')
```

## duo.get_grant_token(auth_url)

> Handles Duo Security MFA stages and returns the grant_token used to finish logging into Synack
>
> | Arguments | Description
> | --- | ---
> | `auth_url` | Duo Security Authentication URL generaated by sending credentials to Synack
>
>> Examples
>> ```python3
>> >>> h.duo.get_grant_token('https:///...duosecurity.com/...')
>> 'Y8....6g'
>> ```

## duo.approve_pending_push(timeout)

> Wait for and approve a single Duo push notification
>
> Polls Duo's device API for pending push notifications and automatically approves the first one found. Useful for automated workflows that need to handle Duo MFA.
>
> | Argument | Type | Default | Description
> | --- | --- | --- | ---
> | `timeout` | int | 30 | Maximum seconds to wait for a push notification
>
> Returns `True` if a push was approved, `False` if timeout or error occurred.
>
>> Examples
>> ```python3
>> >>> h.duo.approve_pending_push(timeout=60)
>> True
>> ```
