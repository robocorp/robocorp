# PyOTP

Generate and verify one-time passwords. It can be used to implement two-factor (2FA) or multi-factor (MFA) authentication methods in your applications.

## Usage

```python
import pyotp

# Create a TOTP object with a secret
totp = pyotp.TOTP(pyotp.random_base32())

print("Current OTP:", totp.now())
```


> AI/LLM's are quite good with `pyotp`.  
> 👉 Try asking [ReMark](https://chat.robocorp.com)

###### Various [snippets](snippets)

- [Generate QR code for TOTP secret](snippets/generate_totp_qr.py)

## Links and references

- [PyPI](https://pypi.org/project/pyotp/)
- [Documentation](https://pyauth.github.io/pyotp/)
- [Api referance](https://pyauth.github.io/pyotp/#module-pyotp)
