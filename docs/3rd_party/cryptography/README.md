# Cryptography

The `cryptography` library is a robust toolkit for implementing secure encryption, decryption, and cryptographic protocols in applications.

## Usage

```python
from cryptography.hazmat.primitives.asymmetric import rsa

private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()
```

> AI/LLM's are quite good with `cryptography`.  
> 👉 Try asking [ReMark](https://chat.robocorp.com)

###### Various [snippets](snippets)

- [Encrypt and decrypt a message using RSA key pairs](snippets/secure_message.py)

## Links and references

- [PyPI](https://pypi.org/project/cryptography/)
- [Documentation](https://cryptography.io/en/latest/)
