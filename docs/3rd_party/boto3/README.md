# Boto3

Create, manage and configure AWS services programatically.

## Usage

```python
import boto3

s3 = boto3.resource('s3')

# Print out bucket names
for bucket in s3.buckets.all():
    print(bucket.name)
```


> AI/LLM's are quite good with `boto3`.  
> 👉 Try asking [ReMark](https://chat.robocorp.com)

###### Various [snippets](snippets)

- [Create a table in DynamoDB](snippets/create_table.py)

## Links and references

- [PyPI](https://pypi.org/project/boto3/)
- [Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [Api referance](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html#api-reference)
