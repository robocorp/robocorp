# Simple Salesforce

Simplified access to Salesforce APIs from Python.

## Usage

```python
from simple_salesforce import Salesforce

sf = Salesforce(username='myemail@example.com', password='password', security_token='token')

# Create a contact
sf.Contact.create({'FirstName': 'John', 'LastName': 'Smith','Email': 'example@example.com'})
```

> AI/LLM's are quite good with `simple-salesforce`.  
> 👉 Try asking [ReMark](https://chat.robocorp.com)

###### Various [snippets](snippets)

- [Find state with most leads](snippets/state_with_most_leads.py)

## Links and references

- [PyPI](https://pypi.org/project/simple-salesforce/)
- [Documentation](https://simple-salesforce.readthedocs.io/en/latest/)
