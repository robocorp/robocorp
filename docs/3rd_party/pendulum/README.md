# Pendulum

Pendulum is a library designed to provide a more intuitive and easier to use interface for working with dates and timezones.

## Usage

```python
import pendulum

dt_toronto = pendulum.datetime(2024, 1, 1, tz='America/Toronto')
dt_vancouver = pendulum.datetime(2024, 1, 1, tz='America/Vancouver')

print(dt_vancouver.diff(dt_toronto).in_hours())
```

> AI/LLM's are quite good with `pendulum`.  
> 👉 Try asking [ReMark](https://chat.robocorp.com)

###### Various [snippets](snippets)

- [Calculate days between dates](snippets/days_between_dates.py)
- [Generate weeks between dates](snippets/weeks_in_interval.py)

## Links and references

- [PyPI](https://pypi.org/project/pendulum/)
- [Documentation](https://pendulum.eustace.io/docs/)
